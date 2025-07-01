import streamlit as st
import pandas as pd

def ler_e_extrair_colunas(arquivo, colunas_necessarias):
    try:
        dataframe = pd.read_csv(arquivo, encoding="ISO-8859-1", delimiter=';', on_bad_lines='skip')
        dataframe.columns = dataframe.columns.str.strip()
        for col in colunas_necessarias:
            if col not in dataframe.columns:
                st.error(f"Coluna '{col}' não encontrada no arquivo. Colunas disponíveis: {dataframe.columns.tolist()}")
                return None
        dataframe["cod_contabil"] = dataframe["cod_contabil"].astype(str).str.strip()
        return dataframe
    except ValueError as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

def processar_arquivos(df_2025, df_2024):
    df_2025 = df_2025[["cod_contabil", "debito_anterior", "credito_anterior"]]
    df_2024 = df_2024[["cod_contabil", "debito_atual", "credito_atual"]]

    df_comparacao = df_2025.merge(df_2024, on="cod_contabil", how="outer")

    df_comparacao["debito_igual"] = df_comparacao["debito_anterior"] == df_comparacao["debito_atual"]
    df_comparacao["credito_igual"] = df_comparacao["credito_anterior"] == df_comparacao["credito_atual"]

    df_comparacao["igualdade_total"] = df_comparacao["debito_igual"] & df_comparacao["credito_igual"]

    df_iguais = df_comparacao[df_comparacao["igualdade_total"]]
    df_diferentes = df_comparacao[~df_comparacao["igualdade_total"]]

    return df_comparacao, df_iguais, df_diferentes

def main():
    st.title("Comparação de Saldos do Balancete")

    st.write("Faça o upload dos arquivos CSV ")

    arquivo_2025 = st.file_uploader("Upload arquivo ano atual ", type="csv")
    arquivo_2024 = st.file_uploader("Upload arquivo ano anterior", type="csv")

    if arquivo_2025 and arquivo_2024:
        colunas_necessarias = ["cod_contabil", "debito_anterior", "credito_anterior", "debito_atual", "credito_atual"]
        df_2025 = ler_e_extrair_colunas(arquivo_2025, colunas_necessarias)
        df_2024 = ler_e_extrair_colunas(arquivo_2024, colunas_necessarias)

        if df_2025 is not None and df_2024 is not None:
            df_comparacao, df_iguais, df_diferentes = processar_arquivos(df_2025, df_2024)

            nome_arquivo_saida = "comparacao_saldos.xlsx"
            with pd.ExcelWriter(nome_arquivo_saida, engine="xlsxwriter") as writer:
                df_comparacao.to_excel(writer, sheet_name="Comparacao Completa", index=False)
                df_iguais.to_excel(writer, sheet_name="Registros Iguais", index=False)
                df_diferentes.to_excel(writer, sheet_name="Registros Diferentes", index=False)

            st.success(f"Arquivo '{nome_arquivo_saida}' gerado com sucesso!")
            st.download_button(label="Download arquivo de comparação", data=open(nome_arquivo_saida, "rb"), file_name=nome_arquivo_saida)

if __name__ == "__main__":
    main()
