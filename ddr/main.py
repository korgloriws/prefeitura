import pandas as pd
import streamlit as st

def ler_e_extrair_colunas(arquivo):
    try:
        dataframe = pd.read_excel(arquivo, usecols=['debito', 'credito', 'ug', 'data_lanc'], dtype=str)
    except ValueError as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None
    
    dataframe['debito'] = pd.to_numeric(dataframe['debito'].str.replace(',', '.').str.strip(), errors='coerce')
    dataframe['credito'] = pd.to_numeric(dataframe['credito'].str.replace(',', '.').str.strip(), errors='coerce')
    
    return dataframe

def processar_arquivos(df_referencia, df_comparacao):
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

    return df_relatorio_completo, df_relatorio_diferencas, df_soma_ug, df_soma_data_lanc

def main():
    st.title("Comparador DDR")
    
    arquivo_referencia = st.file_uploader("Envie o arquivo 62", type=["xlsx"])
    arquivo_comparacao = st.file_uploader("Envie o arquivo 82", type=["xlsx"])
    
    if arquivo_referencia is not None and arquivo_comparacao is not None:
        df_referencia = ler_e_extrair_colunas(arquivo_referencia)
        df_comparacao = ler_e_extrair_colunas(arquivo_comparacao)
        
        if df_referencia is not None and df_comparacao is not None:
            df_relatorio_completo, df_relatorio_diferencas, df_soma_ug, df_soma_data_lanc = processar_arquivos(df_referencia, df_comparacao)
            
            with pd.ExcelWriter('relatorio_comparacoes.xlsx', engine='openpyxl') as writer:
                df_relatorio_completo.to_excel(writer, sheet_name='Comparação Completa', index=False)
                df_relatorio_diferencas.to_excel(writer, sheet_name='Diferenças', index=False)
                df_soma_ug.to_excel(writer, sheet_name='Soma por UG', index=False)
                df_soma_data_lanc.to_excel(writer, sheet_name='Soma por Data Lanç', index=False)
            
            st.success("Relatórios gerados com sucesso.")
            st.download_button(label="Baixar Relatório Completo", data=open('relatorio_comparacoes.xlsx', 'rb'), file_name='relatorio_comparacoes.xlsx')

if __name__ == "__main__":
    main()
