import streamlit as st
import pdfplumber
import pandas as pd
import re
import time
from collections import Counter

def br_to_float(s: str) -> float | None:
    if not s:
        return None
    try:
        return float(s.replace('.', '').replace(',', '.'))
    except ValueError:
        return None

def extrair_valores_cemig(up_file) -> pd.DataFrame:

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(up_file.read())
        tmp_path = tmp.name

    registros = []
    t0 = time.perf_counter()
    with pdfplumber.open(tmp_path) as pdf:
        for n, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text() or ""
            if n == 1:
                print("\n======= TEXTO BRUTO DA PRIMEIRA PÁGINA (pdfplumber) =======\n")
                print(texto)
                print("\n======= FIM DO TEXTO DA PRIMEIRA PÁGINA =======\n")

            contextos = {}

            contextos['total_a_pagar'] = []
            for linha in texto.splitlines():
                if re.search(r'total\s*a\s*pagar', linha, re.I):
                    contextos['total_a_pagar'] += re.findall(r'([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})', linha)
                    contextos['total_a_pagar'] += re.findall(r'R\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})', linha)

            contextos['total'] = []
            for linha in texto.splitlines():
                if re.search(r'total', linha, re.I):
                    contextos['total'] += re.findall(r'([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})', linha)

            contextos['valor_a_pagar'] = []
            for linha in texto.splitlines():
                if re.search(r'valor\s*a\s*pagar', linha, re.I):
                    contextos['valor_a_pagar'] += re.findall(r'([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})', linha)
                    contextos['valor_a_pagar'] += re.findall(r'R\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2})', linha)
            print(f"Candidatos por contexto:")
            for k, v in contextos.items():
                print(f"  {k}: {v}")
  
            all_candidates = []
            for v in contextos.values():
                all_candidates.extend([br_to_float(x) for x in v if br_to_float(x) is not None])

            context_count = Counter()
            for val in set(all_candidates):
                for v in contextos.values():
                    if val in [br_to_float(x) for x in v if br_to_float(x) is not None]:
                        context_count[val] += 1
            print(f"Candidatos a Total a Pagar (por contextos): {context_count}")
            total_pagar = None

            candidatos_3 = [val for val, count in context_count.items() if count == 3]
            if candidatos_3:
                total_pagar = max(candidatos_3)
                print(f"Total a Pagar identificado (aparece nos 3 contextos): {total_pagar}")
            else:

                candidatos_2 = [val for val, count in context_count.items() if count == 2]
                if candidatos_2:
                    total_pagar = max(candidatos_2)
                    print(f"Total a Pagar identificado (aparece em 2 contextos): {total_pagar}")
                elif context_count:

                    total_pagar = max(context_count, key=lambda x: context_count[x])
                    print(f"Total a Pagar fallback (mais frequente): {total_pagar}")

            contextos_irpj = {}

            contextos_irpj['irpj'] = []
            for m in re.finditer(r'ImpostoRetido-IRPJ\s*(\d{2,6})', texto):
                num = m.group(1)
                if len(num) > 2:
                    contextos_irpj['irpj'].append(float(num[:-2] + '.' + num[-2:]))
                else:
                    contextos_irpj['irpj'].append(float('0.' + num.zfill(2)))

            contextos_irpj['retencao'] = []
            for m in re.finditer(r'Reten[çc][aã]o de 1,2% valorR\$\s*(\d{2,6})', texto, re.I):
                num = m.group(1)
                if len(num) > 2:
                    contextos_irpj['retencao'].append(float(num[:-2] + '.' + num[-2:]))
                else:
                    contextos_irpj['retencao'].append(float('0.' + num.zfill(2)))
            print(f"Candidatos IRPJ por contexto:")
            for k, v in contextos_irpj.items():
                print(f"  {k}: {v}")

            all_irpj = []
            for v in contextos_irpj.values():
                all_irpj.extend(v)
            irpj_count = Counter()
            for val in set(all_irpj):
                for v in contextos_irpj.values():
                    if val in v:
                        irpj_count[val] += 1
            print(f"Candidatos a IRPJ (por contextos): {irpj_count}")
            imposto_irpj = None
            candidatos_irpj_2 = [val for val, count in irpj_count.items() if count == 2]
            if candidatos_irpj_2:
                imposto_irpj = max(candidatos_irpj_2)
                print(f"Imposto Retido IRPJ identificado (aparece nos 2 contextos): {imposto_irpj}")
            elif irpj_count:
                imposto_irpj = max(irpj_count, key=lambda x: irpj_count[x])
                print(f"Imposto Retido IRPJ fallback (mais frequente): {imposto_irpj}")
   
            irpj_calculado = None
            if total_pagar is not None:
                irpj_calculado = round(total_pagar * 0.012, 2)
                if imposto_irpj is not None and abs(imposto_irpj - irpj_calculado) > 0.01:
                    print(f"ATENÇÃO: IRPJ extraído ({imposto_irpj}) difere do calculado ({irpj_calculado})!")
            if total_pagar is not None or imposto_irpj is not None:
                registros.append({
                    "Página": n,
                    "Total a Pagar (R$)": total_pagar,
                    "Imposto Retido IRPJ": imposto_irpj,
                    "IRPJ 1,2% calculado": irpj_calculado
                })
    st.info(f"⏱️ Processadas {len(registros)} páginas em "
            f"{time.perf_counter()-t0:.1f}s")
    return pd.DataFrame(registros)

def main():
    st.title("Extrair valores de notas CEMIG ")
    up = st.file_uploader("Selecione o PDF da CEMIG", type=["pdf"])
    if not up:
        return
    with st.spinner("Processando documento…"):
        df = extrair_valores_cemig(up)
    if df.empty:
        st.warning("Nenhum valor encontrado no documento.")
        return
    st.subheader("Valores encontrados por página")
    st.dataframe(
        df.style.format({
            "Total a Pagar (R$)": lambda v: f"R$ {v:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.') if pd.notnull(v) else "",
            "Imposto Retido IRPJ": lambda v: f"R$ {v:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.') if pd.notnull(v) else "",
            "IRPJ 1,2% calculado": lambda v: f"R$ {v:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.') if pd.notnull(v) else ""
        }),
        hide_index=True, use_container_width=True,
    )
    total_valor = df["Total a Pagar (R$)"].sum(skipna=True)
    total_irpj = df["Imposto Retido IRPJ"].sum(skipna=True)
    total_irpj_calc = df["IRPJ 1,2% calculado"].sum(skipna=True)
    total_valor_fmt = f"R$ {total_valor:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.')
    total_irpj_fmt = f"R$ {total_irpj:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.')
    total_irpj_calc_fmt = f"R$ {total_irpj_calc:,.2f}".replace(',', '·').replace('.', ',').replace('·', '.')
    st.success(f"**Total a Pagar (R$):** {total_valor_fmt}")
    st.success(f"**Total Imposto Retido IRPJ:** {total_irpj_fmt}")
    st.info(f"**Total IRPJ 1,2% calculado:** {total_irpj_calc_fmt}")

if __name__ == "__main__":
    main()
