# comparador_pcasp.py
import streamlit as st
import pandas as pd
from io import BytesIO


def clean_conta(col: pd.Series) -> pd.Series:

    return (
        col.astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .str.zfill(9)
    )

def gerar_relatorios(plano_df: pd.DataFrame,
                     stn_df: pd.DataFrame,
                     tce_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    comp1 = plano_df.loc[:, ["cod_contabil_9", "codigo_pcasp", "codigo_tce"]].copy()
    comp1["STATUS_PCASP"] = comp1.apply(
        lambda r: "OK" if r["cod_contabil_9"] == r["codigo_pcasp"] else "DIVERGENTE",
        axis=1,
    )
    comp1["STATUS_TCE"] = comp1.apply(
        lambda r: "OK" if r["cod_contabil_9"] == r["codigo_tce"] else "DIVERGENTE",
        axis=1,
    )


    pcasp_set = set(plano_df["codigo_pcasp"])
    stn_set   = set(stn_df["conta_clean"])
    todos_codigos = sorted(pcasp_set | stn_set)

    comp2 = pd.DataFrame(
        {
            "codigo_pcasp": todos_codigos,
            "SICOF": [c in pcasp_set for c in todos_codigos],
            "STN":   [c in stn_set   for c in todos_codigos],
        }
    )
    comp2["STATUS"] = comp2.apply(
        lambda r: "OK"               if r["SICOF"] and r["STN"]
        else "Faltando no STN"       if r["SICOF"]
        else "Faltando no SICOF",
        axis=1,
    )


    tce_set = set(tce_df["conta_clean"])
    todos_codigos = sorted(set(plano_df["codigo_tce"]) | tce_set)

    comp3 = pd.DataFrame(
        {
            "codigo_tce": todos_codigos,
            "SICOF": [c in plano_df["codigo_tce"].values for c in todos_codigos],
            "TCE":   [c in tce_set for c in todos_codigos],
        }
    )
    comp3["STATUS"] = comp3.apply(
        lambda r: "OK"             if r["SICOF"] and r["TCE"]
        else "Faltando no TCE"     if r["SICOF"]
        else "Faltando no SICOF",
        axis=1,
    )

    return comp1, comp2, comp3


def main():

    st.title("Comparador de PCASPs")

    plano_file = st.file_uploader("Plano de Contas SICOF (.xlsx)", type="xlsx")
    tce_file   = st.file_uploader("PCASP TCE (.xlsx)",             type="xlsx")
    stn_file   = st.file_uploader("PCASP STN (.xlsx)",             type="xlsx")

    if plano_file and tce_file and stn_file:

        plano_df = pd.read_excel(plano_file, dtype=str)
        tce_df   = pd.read_excel(tce_file,   dtype=str)
        stn_df   = pd.read_excel(stn_file,   dtype=str)


        plano_df = plano_df[plano_df["tipo_conta"].astype(str).str.strip() == "5"].copy()
        plano_df["cod_contabil_9"] = (
            plano_df["cod_contabil"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str[:9]
            .str.zfill(9)
        )
        plano_df["codigo_pcasp"] = plano_df["codigo_pcasp"].astype(str).str.zfill(9)
        plano_df["codigo_tce"]   = plano_df["codigo_tce"].astype(str).str.zfill(9)


        stn_df["conta_clean"] = clean_conta(stn_df["Conta"])
        tce_df["conta_clean"] = clean_conta(tce_df["CONTA"])


        comp1, comp2, comp3 = gerar_relatorios(plano_df, stn_df, tce_df)


        st.subheader("Comparação 1 – SICOF (interna)")
        st.dataframe(comp1, use_container_width=True)

        st.subheader("Comparação 2 – SICOF × PCASP STN")
        st.dataframe(comp2, use_container_width=True)

        st.subheader("Comparação 3 – SICOF × PCASP TCE")
        st.dataframe(comp3, use_container_width=True)


        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            comp1.to_excel(writer, index=False, sheet_name="Comparacao_1_SICOF")
            comp2.to_excel(writer, index=False, sheet_name="Comparacao_2_STN")
            comp3.to_excel(writer, index=False, sheet_name="Comparacao_3_TCE")
        buffer.seek(0)

        st.download_button(
            label=" Baixar relatório completo (.xlsx)",
            data=buffer,
            file_name="comparacao_pcasp.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info(" Carregue os três arquivos para iniciar as comparações.")


if __name__ == "__main__":
    main()
