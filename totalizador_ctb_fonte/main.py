import streamlit as st
import pandas as pd
from io import BytesIO

def processar_arquivos(arquivos):
    df_final = pd.DataFrame()

    for arquivo in arquivos:
        df = pd.read_excel(arquivo)
        
        if "fonte" in df.columns and "saldo_final" in df.columns:
            df_grouped = df.groupby("fonte", as_index=False)["saldo_final"].sum()

            if df_final.empty:
                df_final = df_grouped
            else:
                df_final = df_final.merge(df_grouped, on="fonte", how="outer", suffixes=("", "_novo"))
                df_final["saldo_final"] = df_final["saldo_final"].fillna(0) + df_final["saldo_final_novo"].fillna(0)
                df_final.drop(columns=["saldo_final_novo"], inplace=True)
        else:
            st.error(f"O arquivo {arquivo.name} não contém as colunas corretas.")

    if not df_final.empty:
        total_geral = df_final["saldo_final"].sum()
        df_final = pd.concat([df_final, pd.DataFrame([{"fonte": "Total Geral", "saldo_final": total_geral}])], ignore_index=True)

    return df_final

def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Consolidado")
    output.seek(0)
    return output

def main():
    st.title("Totalizador CTB por Fonte")
    st.write("Faça upload de até 6 arquivos no formato `.xlsx` para consolidar os dados.")
    arquivos = st.file_uploader("Selecione os arquivos", type=["xlsx"], accept_multiple_files=True)

    if arquivos and len(arquivos) <= 6:
        if st.button("Gerar Arquivo Consolidado"):
            df_resultado = processar_arquivos(arquivos)

            if not df_resultado.empty:
                st.success("Arquivo consolidado gerado com sucesso!")
                excel_bytes = converter_para_excel(df_resultado)
                st.download_button(
                    label="Baixar Arquivo Consolidado",
                    data=excel_bytes,
                    file_name="consolidado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.warning("Nenhum dado válido foi encontrado nos arquivos enviados.")

if __name__ == "__main__":
    main()
