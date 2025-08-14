import re
import io
from datetime import date, datetime
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


APP_NAME = "Tester de Mapeamento de Receita (Texto de Extrato)"


def get_receita_template_df() -> pd.DataFrame:
    rows = [
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM ITR", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM IPVA", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM ITCMD", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM IPI-EXP", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM ICMS", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM FPE", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIGEM FPM", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "ORIG LC 198/23", "prevista": "", "realizada": ""},
        {"categoria": "IMPOSTOS", "descricao": "OUTROS", "prevista": "", "realizada": ""},
        {"categoria": "RENDIMENTOS", "descricao": "RENDIMENTOS", "prevista": "", "realizada": ""},
        {"categoria": "OUTROS", "descricao": "Editável", "prevista": "", "realizada": ""},
    ]
    return pd.DataFrame(rows, columns=["categoria", "descricao", "prevista", "realizada"])


RECEITA_BANK_PATTERNS: Dict[Tuple[str, str], List[str]] = {
    ("IMPOSTOS", "ORIGEM ITR"): [r"\bITR\b"],
    ("IMPOSTOS", "ORIGEM IPVA"): [r"\bIPVA\b"],
    ("IMPOSTOS", "ORIGEM ITCMD"): [r"\bITCMD\b"],
    ("IMPOSTOS", "ORIGEM IPI-EXP"): [r"\bIPI[- ]?EXP\b"],
    ("IMPOSTOS", "ORIGEM ICMS"): [r"RECEBIMENTO DE ICMS", r"\bICMS\b"],
    ("IMPOSTOS", "ORIGEM FPM"): [r"FPE/FPM", r"\bFPM\b"],
}


def parse_ptbr_money(value: str) -> float:
    try:
        s = str(value).replace(" ", "").replace("R$", "").strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return float(s)
    except Exception:
        return 0.0


def format_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def map_receita_from_text(day: date, raw_text: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    target_date_str = day.strftime("%d/%m/%Y")
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    date_re = re.compile(r"^(\d{2}/\d{2}/\d{4})\b")
    money_re = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*[CD]?")

    totals_by_key: Dict[Tuple[str, str], float] = {}
    matches_detail: List[Dict[str, str]] = []  # type: ignore[type-arg]

    for line in lines:
        dm = date_re.match(line)
        if not dm or dm.group(1) != target_date_str:
            continue
        if line.rstrip().endswith(" D"):
            continue
        mvals = money_re.findall(line)
        if not mvals:
            continue
        amount = parse_ptbr_money(mvals[-1])
        if amount <= 0:
            continue
        for (categoria, descricao), patterns in RECEITA_BANK_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, line, flags=re.IGNORECASE):
                    totals_by_key[(categoria, descricao)] = totals_by_key.get((categoria, descricao), 0.0) + amount
                    matches_detail.append({
                        "data": target_date_str,
                        "categoria": categoria,
                        "descricao": descricao,
                        "valor": format_brl(amount),
                        "linha": line,
                        "padrao": pat,
                    })
                    break

    out = get_receita_template_df()
    for (categoria, descricao), total in totals_by_key.items():
        mask = (
            out["categoria"].astype(str).str.upper().str.strip().eq(categoria)
            & out["descricao"].astype(str).str.upper().str.strip().eq(descricao)
        )
        val_str = format_brl(total)
        if mask.any():
            idx = out.index[mask][0]
            out.at[idx, "realizada"] = val_str
        else:
            out = pd.concat([
                out,
                pd.DataFrame([{ "categoria": categoria, "descricao": descricao, "prevista": "", "realizada": val_str }])
            ], ignore_index=True)

    matches_df = pd.DataFrame(matches_detail, columns=["data", "categoria", "descricao", "valor", "padrao", "linha"]) if matches_detail else pd.DataFrame(columns=["data", "categoria", "descricao", "valor", "padrao", "linha"])
    return out, matches_df


def main():
    st.markdown(f"### {APP_NAME}")
    st.caption("Faça upload do PDF do extrato ou cole o texto do extrato. Informe a data alvo para mapear apenas as linhas desse dia.")

    target_day = st.date_input("Data alvo", value=date.today())

    uploaded_pdf = st.file_uploader("Selecione o PDF do extrato bancário", type=["pdf"])

    raw_text = ""
    if uploaded_pdf is not None:
        data_bytes = uploaded_pdf.read()
        try:
            import pdfplumber  # type: ignore
            lines: List[str] = []
            with pdfplumber.open(io.BytesIO(data_bytes)) as pdf:
                for page in pdf.pages:
                    try:
                        text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                    except Exception:
                        text = page.extract_text() or ""
                    for ln in text.splitlines():
                        ln = ln.strip()
                        if ln:
                            lines.append(ln)
            raw_text = "\n".join(lines)
            st.success(f"PDF lido com sucesso. {len(lines)} linhas extraídas.")
        except Exception as e:
            st.error(f"Falha ao ler PDF: {e}")
    else:
        st.info("Opcionalmente, cole o texto do extrato abaixo para testar sem PDF.")
        sample = (
            "08/08/2025 0000 14011 683 ITR 350 9.615,65 C\n"
            "11/08/2025 0000 14011 639 IPVA 350 14.975,87 C\n"
            "12/08/2025 0000 14011 638 ITCMD 350 99.854,71 C\n"
            "05/08/2025 0000 14011 831 RECEBIMENTO DE ICMS 350 1.218.332,52 C\n"
            "08/08/2025 0000 14011 952 FPE/FPM 350 3.695.338,68 C\n"
        )
        raw_text = st.text_area("Texto do extrato (cole aqui)", height=180, value=sample)

    if raw_text.strip():
        out_df, dbg_df = map_receita_from_text(target_day, raw_text)

        st.markdown("**Resultado mapeado (espelho da tabela de Receita)**")
        st.dataframe(out_df, use_container_width=True, hide_index=True)

        with st.expander("Linhas/ocorrências detectadas", expanded=False):
            if not dbg_df.empty:
                st.dataframe(dbg_df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma ocorrência mapeada para a data alvo.")
    else:
        st.warning("Nenhum conteúdo disponível (PDF não lido e área de texto vazia).")


if __name__ == "__main__":
    main()


