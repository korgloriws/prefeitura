import streamlit as st
import pandas as pd
import numpy as np
import base64
import io

def get_table_download_link(df, filename = 'data', filetype = 'csv'):
    if filetype == 'csv':
        data = df.to_csv(index=False)
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Baixar {filename}.csv</a>'
    elif filetype == 'xlsx':
        towrite = io.BytesIO()
        downloaded_file = df.to_excel(towrite, index=False)  
        towrite.seek(0)
        b64 = base64.b64encode(towrite.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Baixar {filename}.xlsx</a>'
    return href

def main():
    st.title("Balancete vs CTB ")

    uploaded_file1 = st.file_uploader("Escolha o arquivo CSV para BALANCETE", type="csv")
    uploaded_file2 = st.file_uploader("Escolha o arquivo CSV para CTB", type="csv")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        df1 = pd.read_csv(uploaded_file1, delimiter=';', on_bad_lines='skip')
        df2 = pd.read_csv(uploaded_file2, delimiter=';', on_bad_lines='skip')

        df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
        df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

        df1 = df1[df1['registro'] == 17]
        df2 = df2[df2['registro'] == 20]

        df1 = df1[['conta', 'fonte', 'saldo_inicial', 'saldo_final']]
        df2 = df2[['conta', 'fonte', 'saldo_inicial', 'saldo_final']]

        df1['conta'] = df1['conta'].astype(str)
        df1['fonte'] = df1['fonte'].astype(str)
        df2['conta'] = df2['conta'].astype(str)
        df2['fonte'] = df2['fonte'].astype(str)

        df1['saldo_inicial'] = df1['saldo_inicial'].str.replace(',', '.').astype(float).abs()
        df1['saldo_final'] = df1['saldo_final'].str.replace(',', '.').astype(float).abs()
        df2['saldo_inicial'] = df2['saldo_inicial'].str.replace(',', '.').astype(float).abs()
        df2['saldo_final'] = df2['saldo_final'].str.replace(',', '.').astype(float).abs()

        df = pd.merge(df1, df2, on=['conta', 'fonte'], how='outer', suffixes=('_df1', '_df2'), indicator=True)

        df_existem_somente_em_um_arquivo = df[df['_merge'] != 'both']
        st.write("Contas/Fontes que existem apenas em um dos arquivos:")
        st.dataframe(df_existem_somente_em_um_arquivo)

        df_existem_em_ambos_arquivos = df[df['_merge'] == 'both']
        df_iguais = df_existem_em_ambos_arquivos[
            np.isclose(df_existem_em_ambos_arquivos['saldo_inicial_df1'], df_existem_em_ambos_arquivos['saldo_inicial_df2'], rtol=1e-05, atol=1e-08) &
            np.isclose(df_existem_em_ambos_arquivos['saldo_final_df1'], df_existem_em_ambos_arquivos['saldo_final_df2'], rtol=1e-05, atol=1e-08)
        ]
        st.write("Contas/Fontes com saldo inicial/final iguais nos dois arquivos:")
        st.dataframe(df_iguais)

        df_diferentes = df_existem_em_ambos_arquivos[
            (~np.isclose(df_existem_em_ambos_arquivos['saldo_inicial_df1'], df_existem_em_ambos_arquivos['saldo_inicial_df2'], rtol=1e-05, atol=1e-08)) |
            (~np.isclose(df_existem_em_ambos_arquivos['saldo_final_df1'], df_existem_em_ambos_arquivos['saldo_final_df2'], rtol=1e-05, atol=1e-08))
        ]
        st.write("Contas/Fontes com saldo inicial/final diferentes nos dois arquivos:")
        st.dataframe(df_diferentes)

        if st.button('Gerar arquivos'):
       
            st.markdown(get_table_download_link(df_existem_somente_em_um_arquivo, filename = 'Existem_Somente_Em_Um_Arquivo', filetype = 'xlsx'), unsafe_allow_html=True)
       
            st.markdown(get_table_download_link(df_existem_em_ambos_arquivos, filename = 'Existem_Em_Ambos_Arquivos', filetype = 'xlsx'), unsafe_allow_html=True)
       
            st.markdown(get_table_download_link(df_diferentes, filename = 'Saldos_Diferentes', filetype = 'xlsx'), unsafe_allow_html=True)
            st.success('Arquivos gerados com sucesso!')

if __name__ == '__main__':
    main()
