import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO

def formatar_valor(valor):
    if pd.isnull(valor):
        return valor 
    try:
        return float(valor)
    except ValueError:
        
        return float(str(valor).replace('.', '').replace(',', '.'))

def formatar_data(data):
    if pd.isnull(data) or not isinstance(data, str):
        return data  
    data = data.replace('/', '')  
    if len(data) == 8 and data.startswith('0'):
        data = data[1:] 
    return data

def adicionar_origem(df, nome_arquivo):
    df['origem'] = nome_arquivo
    return df

def encontrar_diferencas(df_base, df_comparacao, colunas_base, colunas_comparacao):
    df_comparacao_renamed = df_comparacao.rename(columns=dict(zip(colunas_comparacao, colunas_base)))
    merged_df = pd.merge(df_base, df_comparacao_renamed, on=colunas_base, how='outer', indicator=True)
    diferencas = merged_df[merged_df['_merge'] != 'both'].drop(columns=['_merge'])
    return diferencas

def main():
    st.title("Comparador LQD")

    with st.form("file_upload"):
        lqd_file = st.file_uploader("Carregar arquivo LQD Dez-23.csv", type=['csv'])
        rel_1162_file = st.file_uploader("Carregar arquivo Rel. 1162 Liquidações dez-23.csv", type=['csv'])
        restos_pagar_file = st.file_uploader("Carregar arquivo restos a pagar não processados dez-23.csv", type=['csv'])
        submitted = st.form_submit_button("Processar arquivos")

    if submitted and lqd_file and rel_1162_file and restos_pagar_file:
        
        lqd_df = pd.read_csv(lqd_file, sep=';', dtype=str, encoding='ISO-8859-1')
        df_1162 = pd.read_csv(rel_1162_file, sep=';', dtype=str, encoding='ISO-8859-1')
        restos_pagar_df = pd.read_csv(restos_pagar_file, sep=';', dtype=str, encoding='ISO-8859-1')

        lqd_df['valor_item_empenho'] = lqd_df['valor_item_empenho'].apply(formatar_valor)
        lqd_df['data_nap'] = lqd_df['data_nap'].apply(formatar_data)
        lqd_df = lqd_df[lqd_df['registro'] == '10'][['uo', 'numero_empenho', 'data_nap', 'numero_nap', 'valor_item_empenho']]
        lqd_df = adicionar_origem(lqd_df, 'LQD')

        df_1162['data_nap'] = df_1162['data_nap'].apply(formatar_data)
        df_1162['valor_item_empenho'] = df_1162['valor_item_empenho'].apply(formatar_valor)
        df_1162 = df_1162[['uo', 'numero_empenho', 'data_nap', 'numero_nap', 'valor_item_empenho']]
        df_1162 = adicionar_origem(df_1162, '1162')

        restos_pagar_df.rename(columns={'num_emp': 'numero_empenho', 'valor_liq_mes': 'valor_item_empenho'}, inplace=True)
        restos_pagar_df['valor_item_empenho'] = restos_pagar_df['valor_item_empenho'].apply(formatar_valor)
        restos_pagar_df = restos_pagar_df[['uo', 'numero_empenho', 'valor_item_empenho']]
        restos_pagar_df = adicionar_origem(restos_pagar_df, 'Restos a Pagar')

        
        colunas_comparacao_lqd_1162 = ['uo', 'numero_empenho', 'data_nap', 'numero_nap', 'valor_item_empenho']
        diferencas_lqd_1162 = encontrar_diferencas(lqd_df, df_1162, colunas_comparacao_lqd_1162, colunas_comparacao_lqd_1162)

        colunas_base_lqd = ['uo', 'numero_empenho', 'valor_item_empenho']
        colunas_comparacao_restos = ['uo', 'numero_empenho', 'valor_item_empenho']
        diferencas_lqd_restos = encontrar_diferencas(lqd_df, restos_pagar_df, colunas_base_lqd, colunas_comparacao_restos)

   
        soma_valor_lqd = lqd_df['valor_item_empenho'].sum()
        soma_valor_1162 = df_1162['valor_item_empenho'].sum()
        soma_valor_restos = restos_pagar_df['valor_item_empenho'].sum()

       
        somas_df = pd.DataFrame({
            'Arquivo': ['LQD', '1162', 'Restos a Pagar'],
            'Soma dos Valores': [soma_valor_lqd, soma_valor_1162, soma_valor_restos]
        })

      
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            diferencas_lqd_1162.to_excel(writer, sheet_name='Diferencas_LQD_1162', index=False)
            diferencas_lqd_restos.to_excel(writer, sheet_name='Diferencas_LQD_Restos', index=False)
            somas_df.to_excel(writer, sheet_name='Soma_Valores', index=False)

        st.success("Relatório gerado com sucesso!")

        
        st.download_button(
            label="Baixar relatório de diferenças",
            data=output.getvalue(),
            file_name="relatorio_diferencas.xlsx",
            mime="application/vnd.ms-excel"
        )


if __name__ == '__main__':
    main()
