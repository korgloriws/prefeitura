import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def ajustar_fonte_recurso(codigo):
    codigo_int = int(codigo)
    if codigo_int > 9999999:
        codigo_int = int(str(codigo_int)[1:])
    codigo_int = codigo_int // 1000 * 1000 
    return codigo_int

def ajustar_valor(valor):
    if isinstance(valor, str):
        valor = valor.replace('.', '')
        valor = valor.replace(',', '.')
    return float(valor)

def main():
    st.title('Rec VS QGR')
    st.write("Por favor, faça o upload dos arquivos Rec e QGR")

    uploaded_file_rec = st.file_uploader("Escolha o arquivo REC", type=["xls",'xlsx'])
    uploaded_file_geral = st.file_uploader("Escolha o arquivo QGR", type=['xls','xlsx'])
    nome_arquivo = st.text_input('Digite o nome do arquivo de saída (sem a extensão .xlsx)')

    if uploaded_file_rec is not None and uploaded_file_geral is not None:
        df_rec = pd.read_excel(uploaded_file_rec)
        df_geral = pd.read_excel(uploaded_file_geral)

        # Verificação de linhas duplicadas
        duplicated_rows = df_rec[df_rec.duplicated(subset=['CODIGO_RECEITA', 'FONTE_RECURSO', 'VR_ARREC_MES_FONTE'])]
        if not duplicated_rows.empty:
            st.write('Aviso: Linhas duplicadas encontradas no arquivo REC para os seguintes conjuntos:')
            for _, row in duplicated_rows.iterrows():
                st.write(f"CODIGO_RECEITA: {row['CODIGO_RECEITA']}, FONTE_RECURSO: {row['FONTE_RECURSO']}, VR_ARREC_MES_FONTE: {row['VR_ARREC_MES_FONTE']}")

        # Continuação da manipulação de dados
        df_rec = df_rec[df_rec['COD_ID'] == 11]
        df_rec = df_rec.replace(np.nan, '0')
        df_geral = df_geral.replace(np.nan, '0')
        df_geral['CODIGO_RECEITA'] = df_geral['CODIGO_RECEITA'].apply(lambda x: x if str(x)[0] == '9' else str(x)[:-2])

        excecoes = [21710010, 21749012, 21759005]
        df_excecoes = df_geral[df_geral['FONTE_RECURSO'].isin(excecoes)]
        df_geral = df_geral[~df_geral['FONTE_RECURSO'].isin(excecoes)]
        
        df_geral['FONTE_RECURSO'] = df_geral['FONTE_RECURSO'].apply(ajustar_fonte_recurso)
        df_geral = pd.concat([df_geral, df_excecoes])
        df_geral['VR_ARREC_MES_FONTE'] = df_geral['VR_ARREC_MES_FONTE'].apply(ajustar_valor)
        df_rec['VR_ARREC_MES_FONTE'] = df_rec['VR_ARREC_MES_FONTE'].apply(ajustar_valor)
        df_geral = df_geral.groupby(['CODIGO_RECEITA', 'FONTE_RECURSO'], as_index=False)['VR_ARREC_MES_FONTE'].sum()

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_geral.to_excel(writer, index=False)
        
        output.seek(0)
        if nome_arquivo:
            nome_arquivo += ".xlsx"
        else:
            nome_arquivo = "resultado_soma.xlsx"
        
        st.download_button(
            label="Baixe o arquivo de saída",
            data=output,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
        for index, row in df_geral.iterrows():
            codigo_receita = row['CODIGO_RECEITA']
            fonte_recurso = row['FONTE_RECURSO']
            valor = row['VR_ARREC_MES_FONTE']
            rec_row = df_rec[(df_rec['CODIGO_RECEITA'] == codigo_receita) & (df_rec['FONTE_RECURSO'] == fonte_recurso)]
            if not rec_row.empty and rec_row['VR_ARREC_MES_FONTE'].values[0] != valor:
                st.write(f'Erro: diferenças encontradas para o CODIGO_RECEITA {codigo_receita} e FONTE_RECURSO {fonte_recurso}. Valor esperado: {valor}, valor encontrado: {rec_row["VR_ARREC_MES_FONTE"].values[0]}')
        else:
            st.write('Nenhum erro encontrado.')

if __name__ == "__main__":
    main()
