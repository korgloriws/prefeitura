import streamlit as st
import pandas as pd
from openpyxl import Workbook


def comparar_arquivos(qgr_df, tabela_fontes_df):
  
    qgr_df = qgr_df[['FONTE_RECURSO', 'CO']].drop_duplicates()
    tabela_fontes_df = tabela_fontes_df[['FONTE_RECURSO', 'CO']].drop_duplicates()


    comparacao_completa = pd.merge(
        qgr_df, 
        tabela_fontes_df, 
        on=['FONTE_RECURSO', 'CO'], 
        how='outer', 
        indicator=True
    )


    corretos = comparacao_completa[comparacao_completa['_merge'] == 'both'].drop(columns=['_merge'])
    

    incorretos = comparacao_completa[comparacao_completa['_merge'] != 'both'].copy()
    incorretos['Presente_em'] = incorretos['_merge'].replace({
        'left_only': 'QGR',
        'right_only': 'Tabela de Fontes'
    }).drop(columns=['_merge'])

    return comparacao_completa, corretos, incorretos


def salvar_resultados_excel(comparacao_completa, corretos, incorretos, caminho_arquivo):
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        comparacao_completa.to_excel(writer, sheet_name='Comparacao Completa', index=False)
        corretos.to_excel(writer, sheet_name='Corretos', index=False)
        incorretos.to_excel(writer, sheet_name='Incorretos', index=False)


def main():
    
    st.title('QGR VS Tabela de Fontes e CO')


    qgr_file = st.file_uploader('Faça o upload do arquivo QGR (xlsx)', type='xlsx')
    tabela_fontes_file = st.file_uploader('Faça o upload do arquivo Tabela de Fontes (xlsx)', type='xlsx')

    if qgr_file and tabela_fontes_file:

        qgr_df = pd.read_excel(qgr_file)
        tabela_fontes_df = pd.read_excel(tabela_fontes_file)


        st.subheader('Dados do arquivo QGR (apenas colunas relevantes)')
        st.write(qgr_df[['FONTE_RECURSO', 'CO']].drop_duplicates().head())

        st.subheader('Dados do arquivo Tabela de Fontes (apenas colunas relevantes)')
        st.write(tabela_fontes_df[['FONTE_RECURSO', 'CO']].drop_duplicates().head())


        if st.button('Comparar Arquivos'):
            
            comparacao_completa, corretos, incorretos = comparar_arquivos(qgr_df, tabela_fontes_df)

        
            st.subheader('Comparação Completa')
            st.write(comparacao_completa)

            st.subheader('Conjuntos Corretos')
            st.write(corretos)

            st.subheader('Conjuntos Incorretos (com indicação de origem)')
            st.write(incorretos)

        
            st.subheader('Baixar Resultado')
            output_filename = 'resultado_comparacao.xlsx'
            salvar_resultados_excel(comparacao_completa, corretos, incorretos, output_filename)

            with open(output_filename, 'rb') as f:
                st.download_button('Baixar arquivo Excel', f, file_name=output_filename)


if __name__ == '__main__':
    main()
