import pandas as pd

def ler_e_extrair_colunas(nome_do_arquivo):
    try:
        dataframe = pd.read_excel(nome_do_arquivo, usecols=['debito', 'credito', 'ug', 'data_lanc'], dtype=str)
    except ValueError as e:
        print(f"Erro ao ler o arquivo {nome_do_arquivo}: {e}")
        return None
    
    
    dataframe['debito'] = pd.to_numeric(dataframe['debito'].str.replace(',', '.').str.strip(), errors='coerce')
    dataframe['credito'] = pd.to_numeric(dataframe['credito'].str.replace(',', '.').str.strip(), errors='coerce')
    
    return dataframe


df_referencia = ler_e_extrair_colunas('62 ......xlsx')
df_comparacao = ler_e_extrair_colunas('82......xlsx')

relatorio_completo = []
relatorio_diferencas = []


for key, df_ref_group in df_referencia.groupby(['ug', 'data_lanc']):
    ug, data_lanc = key
    df_comp_group = df_comparacao[(df_comparacao['ug'] == ug) & (df_comparacao['data_lanc'] == data_lanc)].reset_index(drop=True)
    df_ref_group = df_ref_group.reset_index(drop=True)
    
    max_len = max(len(df_ref_group), len(df_comp_group))
    for index in range(max_len):
        if index < len(df_ref_group) and index < len(df_comp_group):
            row_ref = df_ref_group.iloc[index]
            row_comp = df_comp_group.iloc[index]

            debito_comp = row_comp['debito']
            credito_comp = row_comp['credito']
            status = 'Diferença encontrada' if (row_ref['debito'] != debito_comp or row_ref['credito'] != credito_comp) else 'Valores iguais'
        elif index < len(df_ref_group):
            row_ref = df_ref_group.iloc[index]
            debito_comp = 'N/A'
            credito_comp = 'N/A'
            status = 'Somente em Referência'
        else:
            continue  
        
        relatorio_completo.append([ug, data_lanc, row_ref['debito'], row_ref['credito'], debito_comp, credito_comp, status])
        if status == 'Diferença encontrada':
            relatorio_diferencas.append([ug, data_lanc, row_ref['debito'], row_ref['credito'], debito_comp, credito_comp, status])

colunas_relatorio = ['ug', 'data_lanc', 'debito_ref', 'credito_ref', 'debito_comp', 'credito_comp', 'status']
df_relatorio_completo = pd.DataFrame(relatorio_completo, columns=colunas_relatorio)
df_relatorio_diferencas = pd.DataFrame(relatorio_diferencas, columns=colunas_relatorio)


df_relatorio_completo[['debito_ref', 'credito_ref', 'debito_comp', 'credito_comp']] = df_relatorio_completo[['debito_ref', 'credito_ref', 'debito_comp', 'credito_comp']].apply(pd.to_numeric, errors='coerce')


df_soma_ug = df_relatorio_completo.groupby('ug')[['debito_ref', 'credito_ref', 'debito_comp', 'credito_comp']].sum().reset_index()


df_soma_data_lanc = df_relatorio_completo.groupby('data_lanc')[['debito_ref', 'credito_ref', 'debito_comp', 'credito_comp']].sum().reset_index()


nome_do_arquivo_excel = 'relatorio_comparacoes.xlsx'
with pd.ExcelWriter(nome_do_arquivo_excel, engine='openpyxl') as writer:
    df_relatorio_completo.to_excel(writer, sheet_name='Comparação Completa', index=False)
    df_relatorio_diferencas.to_excel(writer, sheet_name='Diferenças', index=False)
    df_soma_ug.to_excel(writer, sheet_name='Soma por UG', index=False)
    df_soma_data_lanc.to_excel(writer, sheet_name='Soma por Data Lanç', index=False)

print(f"Relatórios exportados para {nome_do_arquivo_excel}.")
