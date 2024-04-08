import csv
import pandas as pd
import streamlit as st

def comparar_dados(balancete_df, plano_contas_df):
    balancete_df['cod_contabil'] = balancete_df['cod_contabil'].astype(str)
    plano_contas_df['PL_COD_CONTABIL'] = plano_contas_df['PL_COD_CONTABIL'].astype(str)
    
   
    balancete_df['debito_atual'] = balancete_df['debito_atual'].str.replace('"', '').str.replace(',', '.').str.replace('.', '', regex=False).astype(float)
    balancete_df['credito_atual'] = balancete_df['credito_atual'].str.replace('"', '').str.replace(',', '.').str.replace('.', '', regex=False).astype(float)

    merged_df = pd.merge(balancete_df, plano_contas_df, how='outer', left_on='cod_contabil', right_on='PL_COD_CONTABIL')

    merged_df['Comparacao'] = 'Correto'
    
    merged_df.loc[
        ((merged_df['debito_atual'] > 0) & (merged_df['PL_NAT_SALDO'] != 'D')) |
        ((merged_df['credito_atual'] > 0) & (merged_df['PL_NAT_SALDO'] != 'C')),
        'Comparacao'
    ] = 'Errado'
    
    colunas_relevantes = ['cod_contabil', 'debito_atual', 'credito_atual', 'PL_COD_CONTABIL', 'PL_NAT_SALDO', 'Comparacao']
    merged_df = merged_df[colunas_relevantes]
    diferencas = merged_df[merged_df['Comparacao'] == 'Errado']
    
    
    missing_in_balancete = merged_df.loc[merged_df['cod_contabil'].isna(), 'PL_COD_CONTABIL']
    missing_in_plano_contas = merged_df.loc[merged_df['PL_COD_CONTABIL'].isna(), 'cod_contabil']

    
    df_missing_in_balancete = pd.DataFrame({
        'Codigo_Contabil': missing_in_balancete,
        'Presente_em': 'Plano de Contas',
        'Faltando_em': 'Balancete'
    })

    df_missing_in_plano_contas = pd.DataFrame({
        'Codigo_Contabil': missing_in_plano_contas,
        'Presente_em': 'Balancete',
        'Faltando_em': 'Plano de Contas'
    })

    
    missing_codes = pd.concat([df_missing_in_balancete, df_missing_in_plano_contas])

    return merged_df, diferencas, missing_codes



def main():
    st.title('Comparação Credito e Débito')

    balancete_file = st.file_uploader("Upload do arquivo Balancete", type=['csv'])
    plano_contas_file = st.file_uploader("Upload do arquivo Plano de Contas", type=['xlsx'])

    if balancete_file and plano_contas_file:
        raw_text = balancete_file.read().decode('ISO-8859-1')
        reader = csv.reader(raw_text.splitlines(), delimiter=';')
        records = list(reader)
        balancete_df = pd.DataFrame.from_records(records[1:], columns=records[0])

        plano_contas_df = pd.read_excel(plano_contas_file, engine='openpyxl')

        resultado_completo, diferencas, codigos_faltantes = comparar_dados(balancete_df, plano_contas_df)

        st.subheader("Resultado Completo")
        st.write(resultado_completo)

        st.subheader("Diferenças Encontradas")
        st.write(diferencas)

        st.subheader("Códigos Contábeis Faltantes")
        st.write(codigos_faltantes)

if __name__ == "__main__":
    main()
