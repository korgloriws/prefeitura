import os
import io
import sqlite3
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
import plotly.express as px
import re
from streamlit.components.v1 import html as components_html
import hashlib


# ------------------------------
# Configurações e utilidades
# ------------------------------

APP_NAME = "Fluxo Diário FUNDEB"


def get_base_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir() -> str:
    path = os.path.join(get_base_dir(), "data")
    os.makedirs(path, exist_ok=True)
    return path


def get_uploads_dir() -> str:
    path = os.path.join(get_base_dir(), "uploads")
    os.makedirs(path, exist_ok=True)
    return path


def get_exports_dir() -> str:
    path = os.path.join(get_base_dir(), "exports")
    os.makedirs(path, exist_ok=True)
    return path


def get_db_path() -> str:
    return os.path.join(get_data_dir(), "fluxo.db")


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with connect_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('receita','despesa')),
                descricao TEXT,
                valor1 REAL DEFAULT 0,
                valor2 REAL DEFAULT 0,
                valor_total REAL GENERATED ALWAYS AS (COALESCE(valor1,0) + COALESCE(valor2,0)) VIRTUAL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_movimentos_data_tipo ON movimentos (data, tipo);")
    ensure_db_schema()


def ensure_db_schema() -> None:
    # Garante coluna 'categoria' para agrupar receitas
    with connect_db() as conn:
        cols = [row[1] for row in conn.execute("PRAGMA table_info('movimentos')").fetchall()]
        if "categoria" not in cols:
            conn.execute("ALTER TABLE movimentos ADD COLUMN categoria TEXT")


def fetch_movimentos(
    start: Optional[date] = None,
    end: Optional[date] = None,
    tipo: Optional[str] = None,
) -> pd.DataFrame:
    query = "SELECT data, tipo, descricao, categoria, valor1, valor2, valor_total, source FROM movimentos WHERE 1=1"
    params = []
    if start is not None:
        query += " AND data >= ?"
        params.append(start.isoformat())
    if end is not None:
        query += " AND data <= ?"
        params.append(end.isoformat())
    if tipo is not None:
        query += " AND tipo = ?"
        params.append(tipo)
    query += " ORDER BY data ASC, tipo ASC, rowid ASC"
    with connect_db() as conn:
        df = pd.read_sql_query(query, conn, params=params, parse_dates=["data"])  
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"]).dt.date
    return df


def replace_movimentos_for_day(day: date, tipo: str, df_rows: pd.DataFrame, source: str) -> None:
    expected_cols = ["descricao", "valor1", "valor2"]
    for col in expected_cols:
        if col not in df_rows.columns:
            df_rows[col] = 0 if col in ("valor1", "valor2") else None

    with connect_db() as conn:
        conn.execute("DELETE FROM movimentos WHERE data = ? AND tipo = ?", (day.isoformat(), tipo))
        if not df_rows.empty:
            to_insert = df_rows.copy()
            to_insert = to_insert[["descricao", "valor1", "valor2"]]
            
            for c in ("valor1", "valor2"):
                to_insert[c] = to_insert[c].apply(_parse_number_value)
            to_insert.insert(0, "tipo", tipo)
            to_insert.insert(0, "data", day.isoformat())
            to_insert["source"] = source
            conn.executemany(
                "INSERT INTO movimentos (data, tipo, descricao, valor1, valor2, source) VALUES (?,?,?,?,?,?)",
                to_insert.values.tolist(),
            )


def replace_receita_for_day(day: date, df_rows: pd.DataFrame, source: str) -> None:
    # df_rows esperado: categoria, descricao, prevista, realizada
    expected_cols = ["categoria", "descricao", "prevista", "realizada"]
    for col in expected_cols:
        if col not in df_rows.columns:
            df_rows[col] = "" if col in ("categoria", "descricao") else 0
    with connect_db() as conn:
        conn.execute("DELETE FROM movimentos WHERE data = ? AND tipo = ?", (day.isoformat(), "receita"))
        if not df_rows.empty:
            to_insert = df_rows.copy()
            to_insert = to_insert[["categoria", "descricao", "prevista", "realizada"]]
            # normaliza números
            to_insert["prevista"] = to_insert["prevista"].apply(_parse_number_value)
            to_insert["realizada"] = to_insert["realizada"].apply(_parse_number_value)
            # monta ordem p/ insert
            values = []
            for _, r in to_insert.iterrows():
                values.append(
                    (
                        day.isoformat(),
                        "receita",
                        str(r["descricao"]).strip(),
                        float(r["prevista"]),
                        float(r["realizada"]),
                        "manual" if not source else source,
                        str(r["categoria"]).strip(),
                    )
                )
            conn.executemany(
                "INSERT INTO movimentos (data, tipo, descricao, valor1, valor2, source, categoria) VALUES (?,?,?,?,?,?,?)",
                values,
            )


def replace_despesa_for_day(day: date, df_rows: pd.DataFrame, source: str) -> None:
    # df_rows esperado: categoria, descricao, prevista, realizada
    expected_cols = ["categoria", "descricao", "prevista", "realizada"]
    for col in expected_cols:
        if col not in df_rows.columns:
            df_rows[col] = "" if col in ("categoria", "descricao") else 0
    with connect_db() as conn:
        conn.execute("DELETE FROM movimentos WHERE data = ? AND tipo = ?", (day.isoformat(), "despesa"))
        if not df_rows.empty:
            to_insert = df_rows.copy()
            to_insert = to_insert[["categoria", "descricao", "prevista", "realizada"]]
            # normaliza números
            to_insert["prevista"] = to_insert["prevista"].apply(_parse_number_value)
            to_insert["realizada"] = to_insert["realizada"].apply(_parse_number_value)
            values = []
            for _, r in to_insert.iterrows():
                values.append(
                    (
                        day.isoformat(),
                        "despesa",
                        str(r["descricao"]).strip(),
                        float(r["prevista"]),
                        float(r["realizada"]),
                        "manual" if not source else source,
                        str(r["categoria"]).strip(),
                    )
                )
            conn.executemany(
                "INSERT INTO movimentos (data, tipo, descricao, valor1, valor2, source, categoria) VALUES (?,?,?,?,?,?,?)",
                values,
            )


def detect_period(periodo: str, base_day: date) -> Tuple[date, date]:
    if periodo == "Hoje":
        return base_day, base_day
    if periodo == "Esta semana":
        start = base_day - timedelta(days=base_day.weekday())
        end = start + timedelta(days=6)
        return start, end
    if periodo == "Este mês":
        start = base_day.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1, day=1)
        else:
            next_month = start.replace(month=start.month + 1, day=1)
        end = next_month - timedelta(days=1)
        return start, end
    return base_day, base_day


# ------------------------------
# Upload e parsing de arquivos
# ------------------------------


def parse_txt_to_df(file_bytes: bytes) -> pd.DataFrame:
    text = file_bytes.decode("utf-8", errors="ignore")
    sample = text[:2048]
    delimiter = None
    for cand in [";", ",", "\t", "|"]:
        if cand in sample:
            delimiter = cand
            break
    try:
        df = pd.read_csv(io.StringIO(text), sep=delimiter if delimiter else None, engine="python")
    except Exception:
        # Fallback: try whitespace
        df = pd.read_csv(io.StringIO(text), sep="\s+", engine="python")

    df = normalize_input_df(df)
    return df


def parse_pdf_to_df(file_bytes: bytes) -> pd.DataFrame:
    try:
        import pdfplumber  # type: ignore
    except Exception:
        st.warning("Leitura de PDF limitada (pdfplumber não instalado). Apenas armazenamento do anexo será feito.")
        return pd.DataFrame(columns=["data", "tipo", "descricao", "valor1", "valor2"])  # empty

    def _dedupe_labels(labels: list[str]) -> list[str]:
        counts: dict[str, int] = {}
        out: list[str] = []
        for lbl in labels:
            base = str(lbl).strip().lower()
            if base == "":
                base = "col"
            if base in counts:
                counts[base] += 1
                out.append(f"{base}_{counts[base]}")
            else:
                counts[base] = 0
                out.append(base)
        return out

    tables: list[pd.DataFrame] = []
    max_cols: int = 0
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            try:
                extracted_tables = page.extract_tables()
            except Exception:
                extracted_tables = []
            for tbl in extracted_tables or []:
                if not tbl:
                    continue
                df = pd.DataFrame(tbl).astype(str)
                # Heurística: tenta identificar cabeçalho na primeira linha
                header = df.iloc[0].astype(str).str.lower().tolist()
                if any("desc" in h for h in header) or any("valor" in h for h in header) or any("data" in h for h in header):
                    df.columns = _dedupe_labels(header)
                    df = df.iloc[1:].reset_index(drop=True)
                else:
                    # renomeia colunas para c0..cn e mantém todas as linhas
                    df.columns = [f"c{i}" for i in range(df.shape[1])]
                tables.append(df)
                max_cols = max(max_cols, df.shape[1])

    if not tables:
        return pd.DataFrame(columns=["data", "tipo", "descricao", "valor1", "valor2"])  # empty

    # Normaliza para mesmo número de colunas e nomes únicos antes de concatenar
    norm_tables: list[pd.DataFrame] = []
    for df in tables:
        df2 = df.copy()
        # padroniza nomes
        if set(df2.columns) - set([f"c{i}" for i in range(df2.shape[1])]):
            # se não está no formato c*, converte
            df2.columns = [f"c{i}" for i in range(df2.shape[1])]
        # ajusta largura
        target_cols = [f"c{i}" for i in range(max_cols)]
        df2 = df2.reindex(columns=target_cols, fill_value=None)
        norm_tables.append(df2)

    try:
        big = pd.concat(norm_tables, ignore_index=True)
    except Exception:
        # fallback: usa somente primeiras colunas comuns
        common_cols = sorted(set.intersection(*(set(t.columns) for t in norm_tables))) if norm_tables else []
        big = pd.concat([t[common_cols] for t in norm_tables], ignore_index=True)

    big.columns = [str(c).strip().lower() for c in big.columns]
    big = normalize_input_df(big)
    return big


def normalize_input_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}
    # mapeamentos comuns
    col_map = {
        "data": None,
        "tipo": None,
        "descricao": None,
        "valor1": None,
        "valor2": None,
    }
    for key in list(cols.keys()):
        if key in ("data", "date", "dia"):
            col_map["data"] = cols[key]
        elif key in ("tipo", "natureza", "classificacao"):
            col_map["tipo"] = cols[key]
        elif key.startswith("desc") or key in ("historico", "histórico"):
            col_map["descricao"] = cols[key]
        elif key in ("valor1", "valor_1", "v1"):
            col_map["valor1"] = cols[key]
        elif key in ("valor2", "valor_2", "v2"):
            col_map["valor2"] = cols[key]
        elif key in ("valor", "valor_total", "vlr", "quantia") and col_map["valor1"] is None:
            col_map["valor1"] = cols[key]

    out = pd.DataFrame()
    # data
    if col_map["data"] and col_map["data"] in df.columns:
        out["data"] = pd.to_datetime(df[col_map["data"]], errors="coerce").dt.date
    else:
        out["data"] = pd.NaT
    # tipo
    if col_map["tipo"] and col_map["tipo"] in df.columns:
        out["tipo"] = df[col_map["tipo"]].astype(str).str.lower().str.strip()
    else:
        out["tipo"] = None
    # descricao
    out["descricao"] = df[col_map["descricao"]] if col_map["descricao"] and col_map["descricao"] in df.columns else None
    # valores
    def to_float(s):
        return _parse_number_value(s)

    out["valor1"] = df[col_map["valor1"]].apply(to_float) if col_map["valor1"] and col_map["valor1"] in df.columns else 0.0
    out["valor2"] = df[col_map["valor2"]].apply(to_float) if col_map["valor2"] and col_map["valor2"] in df.columns else 0.0

    # saneia campos
    out["descricao"] = out["descricao"].astype(str).fillna("").str.strip()
    # limita tipo aos aceitos
    out["tipo"] = out["tipo"].where(out["tipo"].isin(["receita", "despesa"]), None)

    return out[["data", "tipo", "descricao", "valor1", "valor2"]]


def _parse_number_value(value) -> float:
    try:
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value)
        if s.strip() == "":
            return 0.0
        s = s.replace(" ", "").replace("R$", "").strip()
        # Heurísticas comuns pt-BR
        # 1) se tem vírgula, tratar vírgula como decimal
        if "," in s and "." in s:
            # remove separadores de milhar (pontos) e troca vírgula por ponto
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            # só vírgula -> decimal
            s = s.replace(".", "").replace(",", ".")
        else:
            # só ponto, assume formato en-US
            pass
        return float(s)
    except Exception:
        return 0.0


# ------------------------------
# UI Helpers
# ------------------------------


def ensure_session_state(day: date) -> None:
    if "receita_df" not in st.session_state:
        st.session_state["receita_df"] = get_receita_template_df()
    if "despesa_df" not in st.session_state:
        st.session_state["despesa_df"] = get_despesa_template_df()
    if st.session_state.get("loaded_day") != day:
        
        df_rec = fetch_movimentos(day, day, "receita")
        df_desp = fetch_movimentos(day, day, "despesa")
        if not df_rec.empty:
            rec_ui = pd.DataFrame(
                {
                    "categoria": df_rec.get("categoria", "").fillna(""),
                    "descricao": df_rec["descricao"].astype(str).fillna(""),
                    "prevista": df_rec["valor1"].apply(lambda x: "" if pd.isna(x) else str(x)),
                    "realizada": df_rec["valor2"].apply(lambda x: "" if pd.isna(x) else str(x)),
                }
            )
            # mescla com template (mantém dtype object para melhor estabilidade do editor)
            st.session_state["receita_df"] = merge_with_template(rec_ui, get_receita_template_df())
        else:
            st.session_state["receita_df"] = get_receita_template_df()
        if not df_desp.empty:
            desp_ui = pd.DataFrame(
                {
                    "categoria": df_desp.get("categoria", "").fillna(""),
                    "descricao": df_desp["descricao"].astype(str).fillna(""),
                    "prevista": df_desp["valor1"].apply(lambda x: "" if pd.isna(x) else str(x)),
                    "realizada": df_desp["valor2"].apply(lambda x: "" if pd.isna(x) else str(x)),
                }
            )
            st.session_state["despesa_df"] = desp_ui
        else:
            st.session_state["despesa_df"] = get_despesa_template_df()
        st.session_state["loaded_day"] = day


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


def get_despesa_template_df() -> pd.DataFrame:
    rows = [
        {"categoria": "FOLHA DE PAGAMENTO", "descricao": "PROFESSOR (70%)", "prevista": "", "realizada": ""},
        {"categoria": "FOLHA DE PAGAMENTO", "descricao": "ADMINISTRATIVO", "prevista": "", "realizada": ""},
        {"categoria": "VALE REFEIÇÃO", "descricao": "PROFESSOR (70%)", "prevista": "", "realizada": ""},
        {"categoria": "VALE REFEIÇÃO", "descricao": "ADMINISTRATIVO", "prevista": "", "realizada": ""},
        {"categoria": "VALE TRANSPORTE", "descricao": "PROFESSOR (70%)", "prevista": "", "realizada": ""},
        {"categoria": "VALE TRANSPORTE", "descricao": "ADMINISTRATIVO", "prevista": "", "realizada": ""},
        {"categoria": "ONG", "descricao": "Editável", "prevista": "", "realizada": ""},
        {"categoria": "CUSTEIO", "descricao": "Editável", "prevista": "", "realizada": ""},
        {"categoria": "OUTROS", "descricao": "Editável", "prevista": "", "realizada": ""},
    ]
    return pd.DataFrame(rows, columns=["categoria", "descricao", "prevista", "realizada"])


def merge_with_template(current_df: pd.DataFrame, template_df: pd.DataFrame) -> pd.DataFrame:
    
    key_cols = ["categoria", "descricao"]
    current = current_df.copy()
    tmpl = template_df.copy()
    
    for c in key_cols:
        if c in current.columns:
            current[c] = current[c].astype(str)
        if c in tmpl.columns:
            tmpl[c] = tmpl[c].astype(str)
    
    current_indexed = current.set_index(key_cols, drop=False)
    rows = []
    for _, trow in tmpl.iterrows():
        key = (str(trow["categoria"]), str(trow["descricao"]))
        if key in current_indexed.index:
            rows.append(current_indexed.loc[key])
        else:
            rows.append(trow)
    merged = pd.DataFrame(rows)
    # adiciona quaisquer linhas extra que não estão no template
    extra_keys = set(current_indexed.index) - set((str(r["categoria"]), str(r["descricao"])) for _, r in tmpl.iterrows())
    if extra_keys:
        merged = pd.concat([merged, current_indexed.loc[list(extra_keys)].reset_index(drop=True)], ignore_index=True)
    # garante colunas na ordem correta
    for col in ["categoria", "descricao", "prevista", "realizada"]:
        if col not in merged.columns:
            merged[col] = ""
    merged = merged[["categoria", "descricao", "prevista", "realizada"]]
    return merged.astype({"categoria": "string", "descricao": "string", "prevista": "string", "realizada": "string"})


def _hash_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _hash_receita_df(df: pd.DataFrame) -> str:
    cols = ["categoria", "descricao", "prevista", "realizada"]
    work = df.copy()
    for c in cols:
        if c not in work.columns:
            work[c] = ""
    # normaliza valores numéricos
    work["prevista"] = work["prevista"].apply(_parse_number_value)
    work["realizada"] = work["realizada"].apply(_parse_number_value)
    # string estável
    lines = [
        f"{str(r['categoria']).strip()}|{str(r['descricao']).strip()}|{float(r['prevista']):.2f}|{float(r['realizada']):.2f}"
        for _, r in work.iterrows()
    ]
    return _hash_text("\n".join(lines))


def _hash_despesa_df(df: pd.DataFrame) -> str:
    # mesma estrutura
    return _hash_receita_df(df)


def ensure_simple_index(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if isinstance(df.index, pd.MultiIndex):
            return df.reset_index(drop=True)
        # Mesmo quando não é MultiIndex, garantimos RangeIndex estável
        return df.reset_index(drop=True)
    except Exception:
        return df.copy()


# ------------------------------
# UI Styling helpers (advanced CSS/HTML)
# ------------------------------


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --primary: #2563EB; /* azul */
            --primary-2: #1D4ED8;
            --success: #16A34A; /* verde */
            --danger: #DC2626;  /* vermelho */
            --muted: #64748B;
            --text: #0F172A;
            --card-bg: #FFFFFF;
            --card-brd: #E2E8F0;
            --shadow: 0 10px 25px rgba(2,6,23,0.06), 0 2px 6px rgba(2,6,23,0.04);
        }
        .block-container { padding-top: 0.5rem; padding-bottom: 2rem; }
        /* HERO */
        .app-hero {
            border-radius: 16px;
            padding: 18px 18px 14px 18px;
            margin: 2px 0 10px 0;
            border: 1px solid var(--card-brd);
            background: radial-gradient(1200px 200px at 10% 0%, rgba(37,99,235,0.12) 0%, transparent 60%),
                        radial-gradient(1200px 200px at 90% 0%, rgba(22,163,74,0.12) 0%, transparent 60%),
                        var(--card-bg);
            box-shadow: var(--shadow);
        }
        .app-hero .title { font-weight: 800; font-size: 22px; color: var(--text); letter-spacing: -0.02em; }
        .app-hero .subtitle { color: var(--muted); font-size: 13px; margin-top: 4px; }
        .badge-row { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
        .badge { border-radius: 999px; padding: 4px 10px; border: 1px solid var(--card-brd); background: #F8FAFC; font-size: 12px; color: var(--text); }
        /* KPI GRID */
        .kpi-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 10px 0 12px 0; }
        .kpi-card { border: 1px solid var(--card-brd); border-radius: 14px; padding: 12px; background: var(--card-bg); box-shadow: var(--shadow); }
        .kpi-label { color: var(--muted); font-size: 12px; margin-bottom: 6px; }
        .kpi-value { font-weight: 800; font-size: 18px; }
        .kpi-receita .kpi-value { color: var(--success); }
        .kpi-despesa .kpi-value { color: var(--danger); }
        .kpi-saldo .kpi-value { color: var(--text); }
        /* Tabs */
        .stTabs [role="tablist"] { gap: 6px; }
        .stTabs [role="tab"] {
            padding: 6px 12px; border-radius: 10px; background: #F8FAFC; border: 1px solid var(--card-brd); color: var(--text);
        }
        .stTabs [aria-selected="true"] { background: linear-gradient(180deg, rgba(37,99,235,0.10), rgba(37,99,235,0.06)); border-color: rgba(37,99,235,0.35); }
        /* Data editor */
        div[data-testid="stDataEditor"] { border: 1px solid var(--card-brd); border-radius: 14px; background: var(--card-bg); box-shadow: var(--shadow); padding: 6px; }
        div[data-testid="stDataEditor"] table { font-size: 13px; }
        div[data-testid="stDataEditor"] thead th { background: #F1F5F9 !important; }
        /* Download buttons */
        div[data-testid="stDownloadButton"] button { width: 100%; border-radius: 10px; padding: 10px 12px; }
        /* Section separators */
        .section-title { font-weight: 700; color: var(--text); margin: 6px 0 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_html_block(html_content: str, height: int | None = None) -> None:
   
    if hasattr(st, "html"):
        try:
            st.html(html_content, height=height)
            return
        except Exception:
            pass
    components_html(html_content, height=height or 160)


def render_hero() -> None:
    html = f"""
   
    """
    render_html_block(html, height=140)


def render_kpis(total_receita: float, total_despesa: float, saldo_inicial: float, saldo_final: float) -> None:
    html = f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-receita">
        <div class="kpi-label">Receita (Realizada)</div>
        <div class="kpi-value">{format_currency(total_receita)}</div>
      </div>
      <div class="kpi-card kpi-despesa">
        <div class="kpi-label">Despesa (Realizada)</div>
        <div class="kpi-value">{format_currency(total_despesa)}</div>
      </div>
      <div class="kpi-card kpi-saldo">
        <div class="kpi-label">Saldo Inicial (dia anterior)</div>
        <div class="kpi-value">{format_currency(saldo_inicial)}</div>
      </div>
      <div class="kpi-card kpi-saldo">
        <div class="kpi-label">Saldo Final do Dia</div>
        <div class="kpi-value">{format_currency(saldo_final)}</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def format_editor_brl(df: pd.DataFrame, columns: list[str] = ["prevista", "realizada"]) -> pd.DataFrame:
    formatted = ensure_simple_index(df).copy()
    for col in columns:
        if col not in formatted.columns:
            formatted[col] = ""
        else:
            def _fmt_cell(v):
                s = str(v).strip()
                if s == "":
                    return ""
                val = _parse_number_value(s)
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            formatted[col] = formatted[col].apply(_fmt_cell)
    return formatted


# ------------------------------
# PDF mapping for Receita (bank statements)
# ------------------------------


RECEITA_BANK_PATTERNS: dict[tuple[str, str], list[str]] = {
    ("IMPOSTOS", "ORIGEM ITR"): [r"\bITR\b"],
    ("IMPOSTOS", "ORIGEM IPVA"): [r"\bIPVA\b"],
    ("IMPOSTOS", "ORIGEM ITCMD"): [r"\bITCMD\b"],
    ("IMPOSTOS", "ORIGEM IPI-EXP"): [r"\bIPI[- ]?EXP\b"],
    ("IMPOSTOS", "ORIGEM ICMS"): [r"RECEBIMENTO DE ICMS", r"\bICMS\b"],
    # Por ora, conforme pedido, mapear FPM a partir de "FPE/FPM"
    ("IMPOSTOS", "ORIGEM FPM"): [r"FPE/FPM", r"\bFPM\b"],
}


def _extract_lines_from_pdf(file_bytes: bytes) -> list[str]:
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return []
    lines: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            try:
                text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            except Exception:
                text = page.extract_text() or ""
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if line:
                    lines.append(line)
    return lines


def autofill_receita_from_bank_pdf(day: date, receita_df: pd.DataFrame, file_bytes: bytes) -> pd.DataFrame:
    target_date_str = day.strftime("%d/%m/%Y")
    lines = _extract_lines_from_pdf(file_bytes)
    if not lines:
        return receita_df

    totals_by_key: dict[tuple[str, str], float] = {}

    date_re = re.compile(r"^(\d{2}/\d{2}/\d{4})\b")
    money_re = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*[CD]?")

    for line in lines:
        dm = date_re.match(line)
        if not dm:
            continue
        if dm.group(1) != target_date_str:
            continue
        # considera apenas créditos (C) quando explícito
        if line.rstrip().endswith(" D"):
            continue
        # tenta capturar último valor monetário
        mvals = money_re.findall(line)
        if not mvals:
            continue
        amount = _parse_number_value(mvals[-1])
        if amount <= 0:
            continue
        for (categoria, descricao), patterns in RECEITA_BANK_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, line, flags=re.IGNORECASE):
                    totals_by_key[(categoria, descricao)] = totals_by_key.get((categoria, descricao), 0.0) + amount
                    break

    if not totals_by_key:
        return receita_df

    updated = receita_df.copy()
    updated = ensure_simple_index(updated)
    if "categoria" not in updated.columns:
        updated["categoria"] = ""
    if "descricao" not in updated.columns:
        updated["descricao"] = ""
    if "prevista" not in updated.columns:
        updated["prevista"] = ""
    if "realizada" not in updated.columns:
        updated["realizada"] = ""

    for (categoria, descricao), total in totals_by_key.items():
        mask = (
            updated["categoria"].astype(str).str.upper().str.strip().eq(categoria)
            & updated["descricao"].astype(str).str.upper().str.strip().eq(descricao)
        )
        val_str = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if mask.any():
            idx = updated.index[mask][0]
            updated.at[idx, "realizada"] = val_str
        else:
            new_row = {"categoria": categoria, "descricao": descricao, "prevista": "", "realizada": val_str}
            updated = pd.concat([updated, pd.DataFrame([new_row])], ignore_index=True)

    # garante template
    updated = merge_with_template(updated, get_receita_template_df())
    return updated


def compute_totals(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    safe = df.copy()
    for c in ("valor1", "valor2"):
        if c not in safe.columns:
            safe[c] = 0.0
    
    safe["valor1"] = safe["valor1"].apply(_parse_number_value)
    safe["valor2"] = safe["valor2"].apply(_parse_number_value)
    return float((safe["valor1"] + safe["valor2"]).sum())


def compute_receita_total(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    if "realizada" in df.columns:
        return float(df["realizada"].apply(_parse_number_value).sum())

    return compute_totals(df)


def compute_despesa_total(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    if "realizada" in df.columns:
        return float(df["realizada"].apply(_parse_number_value).sum())
    if "valor2" in df.columns:
        return float(df["valor2"].apply(_parse_number_value).sum())
    return compute_totals(df)


def format_currency(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def export_excel(receita_form: pd.DataFrame, despesa_form: pd.DataFrame, resumo_diario: pd.DataFrame) -> Tuple[bytes, str]:
    buffer = io.BytesIO()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorio_fluxo_{ts}.xlsx"
    # garante índices simples e colunas esperadas
    rf = ensure_simple_index(receita_form).copy()
    df = ensure_simple_index(despesa_form).copy()
    rd = ensure_simple_index(resumo_diario).copy()
    for c in ["categoria", "descricao", "prevista", "realizada"]:
        if c not in rf.columns:
            rf[c] = ""
        if c not in df.columns:
            df[c] = ""
    rf = rf[["categoria", "descricao", "prevista", "realizada"]]
    df = df[["categoria", "descricao", "prevista", "realizada"]]
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        rf.to_excel(writer, sheet_name="Receita (dia)", index=False)
        df.to_excel(writer, sheet_name="Despesa (dia)", index=False)
        rd.to_excel(writer, sheet_name="Resumo por Dia", index=False)
    buffer.seek(0)

    return buffer.getvalue(), filename


def _format_cell_money_from_text(text_value: str) -> str:
    if text_value is None:
        return ""
    s = str(text_value).strip()
    if s == "":
        return ""
    return format_currency(_parse_number_value(s))


def export_pdf_day(
    day: date,
    receita_df: pd.DataFrame,
    despesa_df: pd.DataFrame,
    total_receita: float,
    total_despesa: float,
    saldo_dia: float,
) -> Tuple[bytes, str]:
    try:
        from fpdf import FPDF  # type: ignore
    except Exception:
        st.warning("Biblioteca fpdf2 não instalada. Instale-a em requirements para exportar PDF.")
        return b"", ""

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Título
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, f"{APP_NAME} - {day.strftime('%d/%m/%Y')}", ln=1)

    # Função para desenhar tabela simples
    def draw_table(title: str, df: pd.DataFrame) -> None:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, title, ln=1)
        headers = ["Categoria", "Descrição", "Prevista", "Realizada"]
        col_widths = [40, 90, 30, 30]
        pdf.set_font("Helvetica", "B", 9)
        for hw, h in zip(col_widths, headers):
            pdf.cell(hw, 7, h, border=1, align="C")
        pdf.ln(7)
        pdf.set_font("Helvetica", "", 9)

        if df is None or df.empty:
            pdf.cell(sum(col_widths), 7, "Sem dados", border=1, align="C", ln=1)
            return

        # garantir colunas
        use_df = df.copy()
        for col in ["categoria", "descricao", "prevista", "realizada"]:
            if col not in use_df.columns:
                use_df[col] = ""

        for _, row in use_df.iterrows():
            cat = str(row["categoria"]) if not pd.isna(row["categoria"]) else ""
            desc = str(row["descricao"]) if not pd.isna(row["descricao"]) else ""
            prev = _format_cell_money_from_text(row["prevista"]) if "prevista" in row else ""
            real = _format_cell_money_from_text(row["realizada"]) if "realizada" in row else ""

            # linha
            pdf.cell(col_widths[0], 7, cat[:35], border=1)
            pdf.cell(col_widths[1], 7, desc[:60], border=1)
            pdf.cell(col_widths[2], 7, prev, border=1, align="R")
            pdf.cell(col_widths[3], 7, real, border=1, align="R")
            pdf.ln(7)

        pdf.ln(2)

    draw_table("Receita", receita_df)
    # totais de receita
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Total Receita do Dia: {format_currency(total_receita)}", ln=1)
    pdf.ln(2)

    draw_table("Despesa", despesa_df)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Total Despesa do Dia: {format_currency(total_despesa)}", ln=1)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Saldo de Dia: {format_currency(saldo_dia)}", ln=1)

    # Finaliza
    result = pdf.output(dest="S")
    if isinstance(result, (bytes, bytearray)):
        content = bytes(result)
    else:
        content = result.encode("latin-1")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fluxo_dia_{day.strftime('%Y%m%d')}_{ts}.pdf"
    return content, filename


# ------------------------------
# Main (Streamlit)
# ------------------------------

def main() -> None:
    inject_styles()
    render_hero()

    init_db()

    base_day = date.today()
    with st.expander("Filtros e importação", expanded=False):
        periodo = st.selectbox("Período", ["Hoje", "Esta semana", "Este mês", "Personalizado"], index=0, help="Escolha o intervalo para consulta e exportação.")
        if periodo == "Personalizado":
            c1, c2 = st.columns(2)
            with c1:
                start = st.date_input("Início", value=base_day.replace(day=1))
            with c2:
                end = st.date_input("Fim", value=base_day)
        else:
            start, end = detect_period(periodo, base_day)

        day = st.date_input("Dia", value=base_day, help="Selecione o dia para lançar e salvar movimentos.")
        uploaded_files = st.file_uploader(
            "Importar arquivos (.txt ou .pdf)", type=["txt", "pdf"], accept_multiple_files=True, help="Arquivos opcionais para pré-preencher."
        )
    ensure_session_state(day)
    st.session_state.setdefault("_last_day_key", day)
    
    if periodo != "Personalizado":
        start, end = detect_period(periodo, day)
    if uploaded_files:
        for uf in uploaded_files:
            data_bytes = uf.read()
            saved_path = os.path.join(get_uploads_dir(), f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uf.name}")
            with open(saved_path, "wb") as f:
                f.write(data_bytes)

            if uf.type == "text/plain" or (uf.name.lower().endswith(".txt")):
                df_imp = parse_txt_to_df(data_bytes)
            elif uf.name.lower().endswith(".pdf"):
                # Primeiro, tentativa de auto-preenchimento específico para Receita a partir do extrato de banco
                try:
                    new_receita = autofill_receita_from_bank_pdf(day, st.session_state["receita_df"], data_bytes)
                    st.session_state["receita_df"] = new_receita
                    # Persiste imediatamente para não ser sobrescrito por fluxos genéricos
                    replace_receita_for_day(day, new_receita, source="pdf-auto")
                    st.success("Receita preenchida automaticamente a partir do PDF do extrato.")
                except Exception:
                    st.warning("Falha ao mapear Receita a partir do PDF. Tentando leitura tabular.")
                # Evita sobrescrever com parse genérico; só use se precisar tratar outras tabelas
                df_imp = pd.DataFrame()
            else:
                df_imp = pd.DataFrame()

           
            if not df_imp.empty:
    
                for tipo_val in ("receita", "despesa"):
                    subset = df_imp[df_imp["tipo"] == tipo_val] if "tipo" in df_imp.columns else pd.DataFrame()
                    if not subset.empty:
                        
                        days_in_subset = subset["data"].dropna().unique().tolist() if "data" in subset.columns else []
                        if days_in_subset:
                            for d in days_in_subset:
                                day_rows = subset[subset["data"] == d][["descricao", "valor1", "valor2"]]
                                replace_movimentos_for_day(d, tipo_val, day_rows, source=f"upload:{uf.name}")
                        else:
                            day_rows = subset[["descricao", "valor1", "valor2"]]
                            replace_movimentos_for_day(day, tipo_val, day_rows, source=f"upload:{uf.name}")

       
        st.session_state.pop("loaded_day", None)
        ensure_session_state(day)
        st.success("Importação concluída.")

    st.subheader("Lançamentos do dia")
    tab_rec, tab_desp = st.tabs(["Receita", "Despesa"])

    with tab_rec:
        st.caption("Preencha Prevista e Realizada usando vírgula para centavos. Categorias padronizadas ajudam no relatório.")
        receita_df: pd.DataFrame = ensure_simple_index(st.session_state["receita_df"])  # evita MultiIndex no editor
        receita_view = format_editor_brl(receita_df)
        edited_receita = st.data_editor(
            receita_view,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=["IMPOSTOS", "RENDIMENTOS", "OUTROS"],
                ),
                "descricao": st.column_config.TextColumn("Descrição"),
                "prevista": st.column_config.TextColumn("Prevista", help="Use vírgula como separador decimal. Ex: 1.234,56"),
                "realizada": st.column_config.TextColumn("Realizada", help="Use vírgula como separador decimal. Ex: 1.234,56"),
            },
            key=f"editor_receita_{day.isoformat()}",
            disabled=False,
        )
      
        # Converte de volta de string BRL para número antes de persistir/calcular
        edited_receita = ensure_simple_index(edited_receita)
        for col in ["prevista", "realizada"]:
            if col in edited_receita.columns:
                edited_receita[col] = edited_receita[col].apply(_parse_number_value)
        new_hash_rec = _hash_receita_df(edited_receita)
        old_hash_rec = st.session_state.get("_hash_rec")
        if new_hash_rec != old_hash_rec:
            replace_receita_for_day(day, edited_receita, source="auto")
            st.session_state["_hash_rec"] = new_hash_rec
        total_receita = compute_receita_total(edited_receita)
        st.metric("Total Receita do Dia (Realizada)", value=format_currency(total_receita))

    with tab_desp:
        st.caption("Preencha Prevista e Realizada usando vírgula para centavos. Categorias padronizadas ajudam no relatório.")
        despesa_df: pd.DataFrame = ensure_simple_index(st.session_state["despesa_df"])  # evita MultiIndex no editor
        despesa_view = format_editor_brl(despesa_df)
        edited_despesa = st.data_editor(
            despesa_view,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=[
                        "FOLHA DE PAGAMENTO",
                        "VALE REFEIÇÃO",
                        "VALE TRANSPORTE",
                        "ONG",
                        "CUSTEIO",
                        "OUTROS",
                    ],
                ),
                "descricao": st.column_config.TextColumn("Descrição"),
                "prevista": st.column_config.TextColumn("Prevista", help="Use vírgula como separador decimal. Ex: 1.234,56"),
                "realizada": st.column_config.TextColumn("Realizada", help="Use vírgula como separador decimal. Ex: 1.234,56"),
            },
            key=f"editor_despesa_{day.isoformat()}",
            disabled=False,
        )
       
        edited_despesa = ensure_simple_index(edited_despesa)
        for col in ["prevista", "realizada"]:
            if col in edited_despesa.columns:
                edited_despesa[col] = edited_despesa[col].apply(_parse_number_value)
        new_hash_desp = _hash_despesa_df(edited_despesa)
        old_hash_desp = st.session_state.get("_hash_desp")
        if new_hash_desp != old_hash_desp:
            replace_despesa_for_day(day, edited_despesa, source="auto")
            st.session_state["_hash_desp"] = new_hash_desp
        total_despesa = compute_despesa_total(edited_despesa)
        st.metric("Total Despesa do Dia (Realizada)", value=format_currency(total_despesa))

    # Calcula saldo do dia anterior (realizado) como saldo inicial
    dia_anterior = day - timedelta(days=1)
    movs_ate_anterior = fetch_movimentos(None, dia_anterior)
    saldo_inicial = 0.0
    if not movs_ate_anterior.empty:
        movs_ate_anterior["realizado"] = movs_ate_anterior["valor2"].apply(_parse_number_value)
        resumo_ant = movs_ate_anterior.groupby(["data", "tipo"], as_index=False)[["realizado"]].sum()
        pivot_ant = resumo_ant.pivot(index="data", columns="tipo", values="realizado").fillna(0.0)
        saldo_inicial = float((pivot_ant.get("receita", 0.0) - pivot_ant.get("despesa", 0.0)).sum())
    saldo_final = saldo_inicial + (total_receita - total_despesa)
    render_kpis(total_receita, total_despesa, saldo_inicial, saldo_final)

    # Auto-save já em uso acima; botões removidos

    st.markdown("---")

    
    filtrado = fetch_movimentos(start, end)
    if not filtrado.empty:
        filtrado["data"] = pd.to_datetime(filtrado["data"]).dt.date

        filtrado["realizado"] = filtrado["valor2"].apply(_parse_number_value)

        resumo = (
            filtrado.groupby(["data", "tipo"], as_index=False)[["realizado"]].sum()
        )
        
        pivot = resumo.pivot(index="data", columns="tipo", values="realizado").fillna(0.0).reset_index()
        pivot["saldo"] = pivot.get("receita", 0.0) - pivot.get("despesa", 0.0)
        pivot["saldo_acumulado"] = pivot["saldo"].cumsum()

        st.subheader("Consulta do período")

        st.markdown("**Resumo diário (Receita x Despesa x Saldo)**")
        pivot_display = pivot.copy()
        if "data" in pivot_display.columns:
            try:
                pivot_display["data"] = pd.to_datetime(pivot_display["data"]).dt.strftime("%d/%m/%Y")
            except Exception:
                pivot_display["data"] = pivot_display["data"].astype(str)
        brl_cols = [c for c in ["receita", "despesa", "saldo", "saldo_acumulado"] if c in pivot_display.columns]
        def _fmt_brl(x):
            try:
                return format_currency(float(x))
            except Exception:
                return ""
        styler = pivot_display.style.format({col: _fmt_brl for col in brl_cols})
        st.dataframe(styler, use_container_width=True, hide_index=True)

   
        st.markdown(" ")
        st.subheader("Comparativo do dia (Receita x Despesa)")
        filtrado_dia = filtrado[filtrado["data"] == day]
        total_rec_dia = float(filtrado_dia.loc[filtrado_dia["tipo"] == "receita", "realizado"].sum()) if not filtrado_dia.empty else 0.0
        total_desp_dia = float(filtrado_dia.loc[filtrado_dia["tipo"] == "despesa", "realizado"].sum()) if not filtrado_dia.empty else 0.0
        if (total_rec_dia + total_desp_dia) > 0:
            df_pie = pd.DataFrame({
                "Tipo": ["Receita (realizada)", "Despesa (realizada)"],
                "Valor": [total_rec_dia, total_desp_dia],
            })
            fig_pie = px.pie(
                df_pie,
                names="Tipo",
                values="Valor",
                hole=0.55,
                color="Tipo",
                color_discrete_map={
                    "Receita (realizada)": "#2E8540",
                    "Despesa (realizada)": "#C0392B",
                },
            )
            fig_pie.update_traces(textposition="inside", textinfo="label+percent", hovertemplate="%{label}<br>Valor: R$ %{value:,.2f}<extra></extra>")
            diff = abs(total_rec_dia - total_desp_dia)
            maior = "Receita" if total_rec_dia >= total_desp_dia else "Despesa"
            fig_pie.update_layout(
                showlegend=False,
                annotations=[
                    dict(text=f"{maior} maior\nDif: {format_currency(diff)}", x=0.5, y=0.5, font_size=14, showarrow=False, align='center')
                ],
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sem valores no dia selecionado.")

        rec_db = fetch_movimentos(day, day, "receita")
        desp_db = fetch_movimentos(day, day, "despesa")
        rec_form = (
            rec_db[["categoria", "descricao", "valor1", "valor2"]]
            .rename(columns={"valor1": "prevista", "valor2": "realizada"})
            if not rec_db.empty else pd.DataFrame(columns=["categoria", "descricao", "prevista", "realizada"])
        )
        desp_form = (
            desp_db[["categoria", "descricao", "valor1", "valor2"]]
            .rename(columns={"valor1": "prevista", "valor2": "realizada"})
            if not desp_db.empty else pd.DataFrame(columns=["categoria", "descricao", "prevista", "realizada"])
        )
        total_rec_db = float(rec_form.get("realizada", pd.Series(dtype=float)).apply(_parse_number_value).sum()) if not rec_form.empty else 0.0
        total_desp_db = float(desp_form.get("realizada", pd.Series(dtype=float)).apply(_parse_number_value).sum()) if not desp_form.empty else 0.0
        saldo_db = total_rec_db - total_desp_db
        excel_bytes, excel_name = export_excel(rec_form, desp_form, pivot)
        pdf_bytes, pdf_name = export_pdf_day(
            day,
            rec_form,
            desp_form,
            total_rec_db,
            total_desp_db,
            saldo_db,
        )
        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button(
                "Baixar relatório .xlsx do período",
                data=excel_bytes,
                file_name=excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with ex2:
            st.download_button(
                "Baixar PDF do dia",
                data=pdf_bytes,
                file_name=pdf_name if pdf_name else "fluxo_dia.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.info("Sem dados no período selecionado.")


if __name__ == "__main__":
    main()


