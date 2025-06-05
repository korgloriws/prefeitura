import pandas as pd


arquivo_2025 = "export(6).csv"
arquivo_2024 = "municipio encerramento 24.csv"

df_2025 = pd.read_csv(arquivo_2025, encoding="ISO-8859-1", delimiter=';', on_bad_lines='skip')
df_2024 = pd.read_csv(arquivo_2024, encoding="ISO-8859-1", delimiter=';', on_bad_lines='skip')

df_2025.columns = df_2025.columns.str.strip()
df_2024.columns = df_2024.columns.str.strip()


colunas_necessarias = ["cod_contabil", "debito_anterior", "credito_anterior", "debito_atual", "credito_atual"]
for col in colunas_necessarias:
    if col not in df_2025.columns:
        raise KeyError(f"Coluna '{col}' não encontrada no arquivo de 2025. Colunas disponíveis: {df_2025.columns.tolist()}")
    if col not in df_2024.columns:
        raise KeyError(f"Coluna '{col}' não encontrada no arquivo de 2024. Colunas disponíveis: {df_2024.columns.tolist()}")


df_2025["cod_contabil"] = df_2025["cod_contabil"].astype(str).str.strip()
df_2024["cod_contabil"] = df_2024["cod_contabil"].astype(str).str.strip()


df_2025 = df_2025[["cod_contabil", "debito_anterior", "credito_anterior"]]
df_2024 = df_2024[["cod_contabil", "debito_atual", "credito_atual"]]


df_comparacao = df_2025.merge(df_2024, on="cod_contabil", how="outer")


df_comparacao["debito_igual"] = df_comparacao["debito_anterior"] == df_comparacao["debito_atual"]
df_comparacao["credito_igual"] = df_comparacao["credito_anterior"] == df_comparacao["credito_atual"]


df_comparacao["igualdade_total"] = df_comparacao["debito_igual"] & df_comparacao["credito_igual"]

df_iguais = df_comparacao[df_comparacao["igualdade_total"]]
df_diferentes = df_comparacao[~df_comparacao["igualdade_total"]]


nome_arquivo_saida = "comparacao_saldos.xlsx"
with pd.ExcelWriter(nome_arquivo_saida, engine="xlsxwriter") as writer:
    df_comparacao.to_excel(writer, sheet_name="Comparacao Completa", index=False)
    df_iguais.to_excel(writer, sheet_name="Registros Iguais", index=False)
    df_diferentes.to_excel(writer, sheet_name="Registros Diferentes", index=False)

print(f"Arquivo '{nome_arquivo_saida}' gerado com sucesso!")
