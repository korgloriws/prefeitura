from __future__ import annotations
import io, re, sys, time
import streamlit as st
import pymupdf as fitz           
from PIL import Image
import pytesseract
import pandas as pd

def br_to_float(s: str) -> float | None:
    if not s:
        return None
    try:

        s = re.sub(r'[^\d,.]', '', s)
        return float(s.replace('.', '').replace(',', '.'))
    except ValueError:
        return None

def ocr_page(pg: fitz.Page, dpi: int = 300) -> str:
    pix = pg.get_pixmap(dpi=dpi, colorspace="rgb")
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="por")

def find_value_at_position(text: str, position: int) -> float | None:

    lines = text.split('\n')
    

    if 0 <= position < len(lines):
        line = lines[position]

        match = re.search(r'(?:R?\$?\s*)?([0-9\.,]+)', line)
        if match:
            return br_to_float(match.group(1))
    return None

def extract_values_from_text(text: str, page_num: int) -> dict:
    values = {
        "Página": page_num,
        "VALOR TOTAL DO SERVIÇO": None,
        "Valor ISS retido": None,
        "Valor IR": None,
        "Valor INSS": None,
        "Valor líquido da NFS-e": None
    }
    

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    

    mapping = {
        "VALOR TOTAL DO SERVIÇO": {"offset": 0, "direction": "same"},     
        "Valor líquido da NFS-e": {"offset": 5, "direction": "above"}   
    }
    
    desc_indices = {}
    for i, line in enumerate(lines):
        for desc in mapping.keys():
            if desc in line:
                desc_indices[desc] = i
    
    for desc, idx in desc_indices.items():
        pattern = mapping[desc]
        target_idx = idx
        
        if pattern["direction"] == "same":

            match = re.search(r'R?\$?\s*([0-9\.,]+)', lines[idx])
            if match:
                values[desc] = br_to_float(match.group(1))
        
        elif pattern["direction"] == "above":

            target_idx = idx - pattern["offset"]
            if target_idx >= 0:
                match = re.search(r'([0-9\.,]+)', lines[target_idx])
                if match:
                    values[desc] = br_to_float(match.group(1))
    

    if values["VALOR TOTAL DO SERVIÇO"] is not None:
        gross_value = values["VALOR TOTAL DO SERVIÇO"]
        values["Valor IR"] = gross_value * 0.048  # 4.8%
        values["Valor ISS retido"] = gross_value * 0.03  # 3%
        values["Valor INSS"] = gross_value * 0.11  # 11%
    
    return values

def extrair_valores(up_file) -> pd.DataFrame:
    pdf_bytes = up_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    registros: list[dict] = []
    t0 = time.perf_counter()


    for i in range(0, len(doc), 2):

        pg1 = doc[i]
        texto1 = pg1.get_text("text") or ""
        if not texto1.strip():
            texto1 = ocr_page(pg1)
        

        texto2 = ""
        if i + 1 < len(doc):
            pg2 = doc[i + 1]
            texto2 = pg2.get_text("text") or ""
            if not texto2.strip():
                texto2 = ocr_page(pg2)
        

        combined_text = texto1 + "\n" + texto2
        

        values = extract_values_from_text(combined_text, i + 1)
        

        if values["VALOR TOTAL DO SERVIÇO"] is not None:
            registros.append(values)

    doc.close()
    st.info(f"⏱️ Processadas {len(registros)} notas fiscais em "
            f"{time.perf_counter()-t0:.1f}s")
    return pd.DataFrame(registros)

def format_currency(value):
    if pd.isna(value):
        return ""
    return f"R$ {value:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.')

def main() -> None:
    st.title("NF-SEPAT - Serviços")

    up = st.file_uploader("Selecione o PDF", type=["pdf"])
    if not up:
        return

    with st.spinner("Processando documento…"):
        df = extrair_valores(up)

    if df.empty:
        st.warning("Nenhum valor encontrado no documento.")
        return

    st.subheader("Valores encontrados")
    
    display_df = df.copy()
    for col in display_df.columns:
        if col != "Página":
            display_df[col] = display_df[col].apply(format_currency)
    
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    totals = {}
    for col in df.columns:
        if col != "Página":
            totals[col] = df[col].sum()

    st.subheader("Totais")
    for field, total in totals.items():
        st.success(f"**{field}:** {format_currency(total)}")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Valores', index=False)
    
    excel_data = excel_buffer.getvalue()
    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="valores_nfse.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main() 