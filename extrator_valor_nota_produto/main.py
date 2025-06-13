
from __future__ import annotations
import io, re, sys, time
import streamlit as st
import pymupdf as fitz           
from PIL import Image
import pytesseract
import pandas as pd



REGEX = re.compile(
    r"VALOR\s+TOTAL\s+DA\s+NOTA" r"(?:\s*[:=]?\s*)?" r"(?:R?\$?\s*)?"
    r"([0-9\.,]{1,20})", flags=re.I | re.S
)

def br_to_float(s: str) -> float | None:
    if not s:
        return None
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except ValueError:
        return None

def ocr_page(pg: fitz.Page, dpi: int = 250) -> str:
    pix = pg.get_pixmap(dpi=dpi, colorspace="rgb")
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="por")



def extrair_valores(up_file) -> pd.DataFrame:
    pdf_bytes = up_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    registros: list[dict] = []
    t0 = time.perf_counter()

    for n, pg in enumerate(doc, start=1):
        texto = pg.get_text("text") or ""
        if not texto.strip():             
            texto = ocr_page(pg)

        for m in REGEX.finditer(texto):
            val = br_to_float(m.group(1))
            if val is not None:
                registros.append({"Página": n, "Valor": val})

    doc.close()
    st.info(f"⏱️ Processadas {len(registros)} ocorrências em "
            f"{time.perf_counter()-t0:.1f}s")
    return pd.DataFrame(registros)



def main() -> None:

    st.title("Soma NF SEPAT Serviços")

    up = st.file_uploader("Selecione o PDF", type=["pdf"])
    if not up:
        return

    with st.spinner("Processando documento…"):
        df = extrair_valores(up)

    if df.empty:
        st.warning("Nenhum valor encontrado no documento.")
        return

    st.subheader("Valores encontrados")
    st.dataframe(
        df.style.format({"Valor": lambda v: f"R$ {v:,.2f}"
                        .replace(',', '·').replace('.', ',').replace('·', '.')}),
        hide_index=True, use_container_width=True,
    )

    total = df["Valor"].sum()
    total_fmt = f"R$ {total:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.')
    st.success(f"**Total no PDF:** {total_fmt}")


if __name__ == "__main__":
    main()
