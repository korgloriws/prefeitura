import pandas as pd
import numpy as np

# Carregar arquivos CSV
df1 = pd.read_csv('BALANCETE MAIO-23.csv', delimiter=';', on_bad_lines='skip')
df2 = pd.read_csv('CTB Maio-23 - Validado.csv', delimiter=';', on_bad_lines='skip')

# Remover colunas 'Unnamed'
df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

# Filtrar os registros com base no valor de 'registro'
df1 = df1[df1['registro'] == 17]
df2 = df2[df2['registro'] == 20]

# Selecionar colunas relevantes para análise
df1 = df1[['conta', 'fonte', 'saldo_inicial', 'saldo_final']]
df2 = df2[['conta', 'fonte', 'saldo_inicial', 'saldo_final']]

# Converter 'conta' e 'fonte' para string em ambos os dataframes
df1['conta'] = df1['conta'].astype(str)
df1['fonte'] = df1['fonte'].astype(str)
df2['conta'] = df2['conta'].astype(str)
df2['fonte'] = df2['fonte'].astype(str)

# Converter os saldos para números, substituindo vírgulas por pontos e aplicando o valor absoluto
df1['saldo_inicial'] = df1['saldo_inicial'].str.replace(',', '.').astype(float).abs()
df1['saldo_final'] = df1['saldo_final'].str.replace(',', '.').astype(float).abs()
df2['saldo_inicial'] = df2['saldo_inicial'].str.replace(',', '.').astype(float).abs()
df2['saldo_final'] = df2['saldo_final'].str.replace(',', '.').astype(float).abs()

# Combinar os dataframes
df = pd.merge(df1, df2, on=['conta', 'fonte'], how='outer', suffixes=('_df1', '_df2'), indicator=True)

# Agora podemos verificar as contas/fontes que existem apenas em um dos arquivos
df_existem_somente_em_um_arquivo = df[df['_merge'] != 'both']
print("Contas/Fontes que existem apenas em um dos arquivos:")
print(df_existem_somente_em_um_arquivo)

# Para as contas/fontes que existem nos dois arquivos, podemos comparar os saldos inicial e final
df_existem_em_ambos_arquivos = df[df['_merge'] == 'both']
print("Contas/Fontes com saldo inicial/final iguais nos dois arquivos:")
print(df_existem_em_ambos_arquivos[np.isclose(df_existem_em_ambos_arquivos['saldo_inicial_df1'], df_existem_em_ambos_arquivos['saldo_inicial_df2'], rtol=1e-05, atol=1e-08) & np.isclose(df_existem_em_ambos_arquivos['saldo_final_df1'], df_existem_em_ambos_arquivos['saldo_final_df2'], rtol=1e-05, atol=1e-08)])

# Filtrar os registros com diferenças nos saldos iniciais e finais
df_diferentes = df_existem_em_ambos_arquivos[
    (~np.isclose(df_existem_em_ambos_arquivos['saldo_inicial_df1'], df_existem_em_ambos_arquivos['saldo_inicial_df2'], rtol=1e-05, atol=1e-08)) |
    (~np.isclose(df_existem_em_ambos_arquivos['saldo_final_df1'], df_existem_em_ambos_arquivos['saldo_final_df2'], rtol=1e-05, atol=1e-08))
]
print("Contas/Fontes com saldo inicial/final diferentes nos dois arquivos:")
print(df_diferentes)

# Salvar o DataFrame 'df_existem_somente_em_um_arquivo' em um arquivo CSV
df_existem_somente_em_um_arquivo.to_csv('Existem_Somente_Em_Um_Arquivo.csv', index=False)

# Salvar o DataFrame 'df_existem_em_ambos_arquivos' em um arquivo CSV
df_existem_em_ambos_arquivos.to_csv('Existem_Em_Ambos_Arquivos.csv', index=False)

# Salvar o DataFrame 'df_diferentes' em um arquivo CSV
df_diferentes.to_csv('Saldos_Diferentes.csv', index=False)
