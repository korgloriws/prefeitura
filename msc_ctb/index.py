import pandas as pd
import streamlit as st
from io import BytesIO
import numpy as np


def tratar_ic3(ic3):
    ic3_str = str(ic3)
    if len(ic3_str) == 8:
        return ic3_str[1:5]  
    elif len(ic3_str) == 7:
        return ic3_str[:4]  
    else:
        return ic3_str  


def tratar_msc(msc_df):


    msc_df['IC3_tratado'] = msc_df['IC3'].apply(tratar_ic3)


    msc_df_filtrado = msc_df[msc_df['Tipo_valor'] == 'ending_balance']


    msc_devedor = msc_df_filtrado[msc_df_filtrado['Natureza_valor'] == 'D']
    msc_credor = msc_df_filtrado[msc_df_filtrado['Natureza_valor'] == 'C']

    devedor_agrupado = msc_devedor.groupby(['CONTA', 'IC3_tratado'])['Valor'].sum().reset_index()
    credor_agrupado = msc_credor.groupby(['CONTA', 'IC3_tratado'])['Valor'].sum().reset_index()

    resultado = pd.merge(devedor_agrupado, credor_agrupado, on=['CONTA', 'IC3_tratado'], suffixes=('_D', '_C'), how='outer').fillna(0)
    resultado['Valor'] = resultado['Valor_D'] - resultado['Valor_C']


    return resultado[['CONTA', 'IC3_tratado', 'Valor']]


def tratar_ctb(ctb_df):


    ctb_df['IC3_tratado'] = ctb_df['IC3'].apply(tratar_ic3)


    ctb_agrupado = ctb_df.groupby(['cod_reduz', 'IC3_tratado'])['Valor'].sum().reset_index()

    return ctb_agrupado[['cod_reduz', 'IC3_tratado', 'Valor']]




def truncar_duas_casas(numero):

    return np.trunc(numero * 100) / 100


def processar_comparacao(msc_df, ctb_df):
    msc_tratado = tratar_msc(msc_df)
    ctb_tratado = tratar_ctb(ctb_df)

    comparacao = pd.merge(
        msc_tratado,
        ctb_tratado,
        left_on=['CONTA', 'IC3_tratado'],
        right_on=['cod_reduz', 'IC3_tratado'],
        suffixes=('_MSC', '_CTB')
    )
    comparacao['Diferenca'] = comparacao['Valor_MSC'] - comparacao['Valor_CTB']

  
    comparacao['Valor_MSC'] = comparacao['Valor_MSC'].apply(truncar_duas_casas)
    comparacao['Valor_CTB'] = comparacao['Valor_CTB'].apply(truncar_duas_casas)
    comparacao['Diferenca'] = comparacao['Diferenca'].apply(truncar_duas_casas)

  
    corretos = comparacao[comparacao['Diferenca'] == 0]
    diferencas = comparacao[comparacao['Diferenca'] != 0]

    return comparacao, corretos, diferencas




def to_excel(df1, df2, df3):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Comparacao Completa', index=False)
        df2.to_excel(writer, sheet_name='Corretos', index=False)
        df3.to_excel(writer, sheet_name='Diferencas', index=False)
    processed_data = output.getvalue()
    return processed_data


def main():
    st.title("MSC VS CTB")

 
    msc_file = st.file_uploader("Carregar o arquivo MSC", type=["xlsx"])
    ctb_file = st.file_uploader("Carregar o arquivo CTB", type=["xlsx"])

    if msc_file and ctb_file:

        msc_df = pd.read_excel(msc_file)
        ctb_df = pd.read_excel(ctb_file)


        comparacao, corretos, diferencas = processar_comparacao(msc_df, ctb_df)


        excel_data = to_excel(comparacao, corretos, diferencas)


        st.success("Processo concluído com sucesso!")
        st.download_button(label="Baixar Comparação Completa", data=excel_data, file_name="resultado_CTB_vs_MSC.xlsx")

if __name__ == '__main__':
    main()
