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
    return abs(float(valor))

def validar_registros_10_11(df_rec):

    discrepancias_internas = []
    
  
    registros_10 = df_rec[df_rec.iloc[:, 0] == 10].copy()  
    registros_11 = df_rec[df_rec.iloc[:, 0] == 11].copy()  
    
    if registros_11.empty or registros_10.empty:
        return discrepancias_internas
    
    
    temp_df = pd.DataFrame({
        'CODIGO_RECEITA': registros_11.iloc[:, 1],  
        'VALOR': registros_11.iloc[:, 10]  
    })
    
  
    registros_11_agrupados = temp_df.groupby('CODIGO_RECEITA')['VALOR'].sum().reset_index()
    registros_11_agrupados.columns = ['CODIGO_RECEITA', 'VALOR_REGISTRO_11']
    
   
    for _, row in registros_11_agrupados.iterrows():
        codigo_receita = row['CODIGO_RECEITA']
        valor_soma_11 = row['VALOR_REGISTRO_11']
        
 
        registro_10 = registros_10[registros_10.iloc[:, 1] == codigo_receita]
        
        if not registro_10.empty:
            valor_registro_10 = registro_10.iloc[0, 6]  
            

            valor_soma_11 = ajustar_valor(valor_soma_11)
            valor_registro_10 = ajustar_valor(valor_registro_10)
            

            if abs(valor_soma_11) != abs(valor_registro_10):
                discrepancias_internas.append({
                    'CODIGO_RECEITA': codigo_receita,
                    'VALOR_REGISTRO_10': valor_registro_10,
                    'SOMA_REGISTROS_11': valor_soma_11,
                    'DIFERENCA': abs(valor_soma_11) - abs(valor_registro_10)
                })
    
    return discrepancias_internas

def main():
    st.title('Rec VS QGR')
    st.write("Por favor, faça o upload dos arquivos Rec e QGR")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file_rec = st.file_uploader("Escolha o arquivo REC", type=["xls", 'xlsx'])
    with col2:
        uploaded_file_geral = st.file_uploader("Escolha o arquivo QGR", type=['xls', 'xlsx'])

    nome_arquivo = st.text_input('Digite o nome do arquivo de saída (sem a extensão .xlsx)')

    if uploaded_file_rec is not None and uploaded_file_geral is not None:
        df_rec = pd.read_excel(uploaded_file_rec)
        df_geral = pd.read_excel(uploaded_file_geral)

        duplicated_rows = df_rec[df_rec.duplicated(subset=['CODIGO_RECEITA', 'FONTE_RECURSO', 'VR_ARREC_MES_FONTE'])]
        if not duplicated_rows.empty:
            st.write('Aviso: Linhas duplicadas encontradas no arquivo REC para os seguintes conjuntos:')
            for _, row in duplicated_rows.iterrows():
                st.write(f"CODIGO_RECEITA: {row['CODIGO_RECEITA']}, FONTE_RECURSO: {row['FONTE_RECURSO']}, VR_ARREC_MES_FONTE: {row['VR_ARREC_MES_FONTE']}")


        st.write("### Validação Interna - Registros 10 vs 11")
        discrepancias_internas = validar_registros_10_11(df_rec)
        
        if discrepancias_internas:
            df_discrepancias_internas = pd.DataFrame(discrepancias_internas)
            df_discrepancias_internas['VALOR_REGISTRO_10'] = df_discrepancias_internas['VALOR_REGISTRO_10'].map('{:,.2f}'.format).str.replace(',', 'X').str.replace('.', ',').str.replace('X', '.')
            df_discrepancias_internas['SOMA_REGISTROS_11'] = df_discrepancias_internas['SOMA_REGISTROS_11'].map('{:,.2f}'.format).str.replace(',', 'X').str.replace('.', ',').str.replace('X', '.')
            df_discrepancias_internas['DIFERENCA'] = df_discrepancias_internas['DIFERENCA'].map('{:,.2f}'.format).str.replace(',', 'X').str.replace('.', ',').str.replace('X', '.')
            df_discrepancias_internas['CODIGO_RECEITA'] = df_discrepancias_internas['CODIGO_RECEITA'].astype(str)
            
            st.write("Discrepâncias encontradas entre registros 10 e 11:")
            st.dataframe(df_discrepancias_internas)
        else:
            st.write('Nenhuma discrepância encontrada entre registros 10 e 11.')

        df_rec = df_rec[df_rec['COD_ID'] == 11]
        df_rec = df_rec.replace(np.nan, '0')
        df_geral = df_geral.replace(np.nan, '0')

        excecoes = [21710010, 21749012, 21759005]
        df_excecoes = df_geral[df_geral['FONTE_RECURSO'].isin(excecoes)]
        df_geral = df_geral[~df_geral['FONTE_RECURSO'].isin(excecoes)]

        df_geral['FONTE_RECURSO'] = df_geral['FONTE_RECURSO'].apply(ajustar_fonte_recurso)
        df_geral = pd.concat([df_geral, df_excecoes])
        df_geral['VR_ARREC_MES_FONTE'] = df_geral['VR_ARREC_MES_FONTE'].apply(ajustar_valor)
        df_rec['VR_ARREC_MES_FONTE'] = df_rec['VR_ARREC_MES_FONTE'].apply(ajustar_valor)

        df_geral = df_geral.groupby(['CODIGO_RECEITA', 'FONTE_RECURSO'], as_index=False)['VR_ARREC_MES_FONTE'].sum()
        df_rec = df_rec.groupby(['CODIGO_RECEITA', 'FONTE_RECURSO'], as_index=False)['VR_ARREC_MES_FONTE'].sum()


        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_geral.to_excel(writer, sheet_name='Resultado_QGR', index=False)
            

            if discrepancias_internas:
                df_discrepancias_internas_excel = pd.DataFrame(discrepancias_internas)
                df_discrepancias_internas_excel.to_excel(writer, sheet_name='Discrepancias_10_11', index=False)

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

        discrepancias = []
        for index, row in df_geral.iterrows():
            codigo_receita = row['CODIGO_RECEITA']
            fonte_recurso = row['FONTE_RECURSO']
            valor_geral = round(row['VR_ARREC_MES_FONTE'], 2)

            rec_row = df_rec[(df_rec['CODIGO_RECEITA'] == codigo_receita) & (df_rec['FONTE_RECURSO'] == fonte_recurso)]

            if not rec_row.empty:
                valor_rec = round(rec_row['VR_ARREC_MES_FONTE'].values[0], 2)
                if abs(valor_rec) != abs(valor_geral):
                    discrepancias.append((codigo_receita, fonte_recurso, abs(valor_geral), abs(valor_rec)))

        if discrepancias:
            df_discrepancias = pd.DataFrame(discrepancias, columns=['CODIGO_RECEITA', 'FONTE_RECURSO', 'Valor QGR', 'Valor REC'])
            df_discrepancias['Valor QGR'] = df_discrepancias['Valor QGR'].map('{:,.2f}'.format).str.replace(',', 'X').str.replace('.', ',').str.replace('X', '.')
            df_discrepancias['Valor REC'] = df_discrepancias['Valor REC'].map('{:,.2f}'.format).str.replace(',', 'X').str.replace('.', ',').str.replace('X', '.')
            df_discrepancias['CODIGO_RECEITA'] = df_discrepancias['CODIGO_RECEITA'].astype(str)
            st.write("Discrepâncias encontradas:")
            st.dataframe(df_discrepancias)

            output_discrepancias = BytesIO()
            with pd.ExcelWriter(output_discrepancias, engine='openpyxl') as writer:
                df_discrepancias.to_excel(writer, index=False)

            output_discrepancias.seek(0)
            nome_relatorio = "relatorio_discrepancias.xlsx"
            
            st.download_button(
                label="Baixe o relatório de discrepâncias",
                data=output_discrepancias,
                file_name=nome_relatorio,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.write('Nenhum erro encontrado.')

if __name__ == "__main__":
    main()
