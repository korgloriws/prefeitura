import streamlit as st
import pandas as pd
import numpy as np
import base64
import io


def format_brazilian_currency(value):
    if pd.isna(value):
        return value
    return f'R$ {value:,.2f}'.replace('.', 'X').replace(',', '.').replace('X', ',')

def is_close(value1, value2, tol=0.001):
    if pd.isna(value1) or pd.isna(value2):
        return False
    return abs(value1 - value2) < tol

def calculate_d_minus_c(df):
    result = []
    grouped = df.groupby(['conta', 'fonte'])
    for name, group in grouped:
        if group['CO'].nunique() > 1:
            c_initial = group[group['natureza_valor'] == 'C']['saldo_inicial'].sum()
            d_initial = group[group['natureza_valor'] == 'D']['saldo_inicial'].sum()
            c_final = group[group['natureza_valor'] == 'C']['saldo_final'].sum()
            d_final = group[group['natureza_valor'] == 'D']['saldo_final'].sum()
            saldo_inicial = d_initial - c_initial
            saldo_final = d_final - c_final
            result.append({
                'conta': name[0],
                'fonte': name[1],
                'saldo_inicial': saldo_inicial,
                'saldo_final': saldo_final
            })
    return pd.DataFrame(result)

def get_table_download_link(df, filename='data', filetype='csv'):
    if filetype == 'csv':
        data = df.to_csv(index=False)
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Baixar {filename}.csv</a>'
    elif filetype == 'xlsx':
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False)
        towrite.seek(0)
        b64 = base64.b64encode(towrite.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Baixar {filename}.xlsx</a>'
    return href

def main():
    st.title("Balancete vs CTB")

    uploaded_file1 = st.file_uploader("Escolha o arquivo Excel para BALANCETE", type="xlsx")
    uploaded_file2 = st.file_uploader("Escolha o arquivo Excel para CTB", type="xlsx")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        df1 = pd.read_excel(uploaded_file1)
        df2 = pd.read_excel(uploaded_file2)

        df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
        df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

        df1 = df1[df1['registro'] == 17]
        df2 = df2[df2['registro'] == 20]

        df1 = df1[['conta', 'fonte', 'CO', 'natureza_valor', 'saldo_inicial', 'saldo_final']]
        df2 = df2[['conta', 'fonte', 'saldo_inicial', 'saldo_final']]

        df1['conta'] = df1['conta'].astype(str)
        df1['fonte'] = df1['fonte'].astype(str)
        df2['conta'] = df2['conta'].astype(str)
        df2['fonte'] = df2['fonte'].astype(str)

        df1['saldo_inicial'] = df1['saldo_inicial'].astype(str).str.replace(',', '.').astype(float)
        df1['saldo_final'] = df1['saldo_final'].astype(str).str.replace(',', '.').astype(float)
        df2['saldo_inicial'] = df2['saldo_inicial'].astype(str).str.replace(',', '.').astype(float)
        df2['saldo_final'] = df2['saldo_final'].astype(str).str.replace(',', '.').astype(float)

        df1_calculated = calculate_d_minus_c(df1)

        df = pd.merge(df1_calculated, df2, on=['conta', 'fonte'], how='outer', suffixes=('_df1', '_df2'), indicator=True)

        df_existem_somente_em_um_arquivo = df[df['_merge'] != 'both']
        df_existem_em_ambos_arquivos = df[df['_merge'] == 'both']

        df_iguais = df_existem_em_ambos_arquivos[
            df_existem_em_ambos_arquivos.apply(lambda row: is_close(row['saldo_inicial_df1'], row['saldo_inicial_df2']) and is_close(row['saldo_final_df1'], row['saldo_final_df2']), axis=1)
        ]

        df_diferentes = df_existem_em_ambos_arquivos[
            ~df_existem_em_ambos_arquivos.apply(lambda row: is_close(row['saldo_inicial_df1'], row['saldo_inicial_df2']) and is_close(row['saldo_final_df1'], row['saldo_final_df2']), axis=1)
        ]

        colunas_renomeadas = {
            'saldo_inicial_df1': 'saldo_inicial_balancete',
            'saldo_final_df1': 'saldo_final_balancete',
            'saldo_inicial_df2': 'saldo_inicial_ctb',
            'saldo_final_df2': 'saldo_final_ctb'
        }
        df_existem_somente_em_um_arquivo.rename(columns=colunas_renomeadas, inplace=True)
        df_iguais.rename(columns=colunas_renomeadas, inplace=True)
        df_diferentes.rename(columns=colunas_renomeadas, inplace=True)

        df_existem_somente_em_um_arquivo[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']] = df_existem_somente_em_um_arquivo[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']].applymap(format_brazilian_currency)
        df_iguais[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']] = df_iguais[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']].applymap(format_brazilian_currency)
        df_diferentes[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']] = df_diferentes[['saldo_inicial_balancete', 'saldo_final_balancete', 'saldo_inicial_ctb', 'saldo_final_ctb']].applymap(format_brazilian_currency)

        st.write("Contas/Fontes que existem apenas em um dos arquivos:")
        st.dataframe(df_existem_somente_em_um_arquivo)

        st.write("Contas/Fontes com saldo inicial/final iguais nos dois arquivos:")
        st.dataframe(df_iguais)

        st.write("Contas/Fontes com saldo inicial/final diferentes nos dois arquivos:")
        st.dataframe(df_diferentes)

        if st.button('Gerar arquivos'):
            st.markdown(get_table_download_link(df_existem_somente_em_um_arquivo, filename='Existem_Somente_Em_Um_Arquivo', filetype='xlsx'), unsafe_allow_html=True)
            st.markdown(get_table_download_link(df_iguais, filename='Existem_Em_Ambos_Arquivos', filetype='xlsx'), unsafe_allow_html=True)
            st.markdown(get_table_download_link(df_diferentes, filename='Saldos_Diferentes', filetype='xlsx'), unsafe_allow_html=True)
            st.success('Arquivos gerados com sucesso!')

if __name__ == '__main__':
    main()
