import streamlit as st
import pandas as pd
import xlwings as xw
import tempfile
import os

def soma_valores_correspondentes(df_csv, codigos_excel, co_excel, fonte_recurso_excel):
    filtro_final = pd.Series([True] * len(df_csv))
    
    filtro_codigos = df_csv['CODIGO_RECEITA'].apply(lambda x: any(str(x).startswith(''.join(filter(str.isdigit, c))) for c in codigos_excel))
    filtro_final &= filtro_codigos
    
    if pd.notna(co_excel):
        filtro_co = (df_csv['CO'] == co_excel)
        filtro_final &= filtro_co

    if pd.notna(fonte_recurso_excel):
        fonte_recurso_vals = [str(f).strip() for f in str(fonte_recurso_excel).split(',')]
        filtro_fonte_recurso = df_csv['FONTE_RECURSO'].apply(lambda x: str(x) in fonte_recurso_vals)
        filtro_final &= filtro_fonte_recurso
    
    soma_valores = df_csv.loc[filtro_final, 'VR_ARREC_MES_FONTE'].sum()
    
    return soma_valores

def processar_arquivos(csv_file, excel_file):
    df_csv = pd.read_csv(csv_file, sep=';', encoding='cp1252', usecols=["CODIGO_RECEITA", "FONTE_RECURSO", "CO", "VR_ARREC_MES_FONTE"])
    df_csv['VR_ARREC_MES_FONTE'] = df_csv['VR_ARREC_MES_FONTE'].str.replace('.', '').str.replace(',', '.').astype(float)

   
    excel_path = tempfile.mktemp(suffix='.xlsx')
    
   
    with open(excel_path, "wb") as tmp:
        tmp.write(excel_file.getvalue())
    
    app = xw.App(visible=False) 
    book = xw.Book(excel_path)
    sheet = book.sheets['Rascunho (2)']

    inicio_linha_excel = 8
    fim_linha_excel = 41

    for i in range(inicio_linha_excel, fim_linha_excel + 1):
        codigo_excel = sheet.range(f'B{i}').value
        co_excel = sheet.range(f'C{i}').value
        fonte_recurso_excel = sheet.range(f'D{i}').value
        
        if not codigo_excel:
            st.write(f"Nenhum código encontrado na linha {i}, pulando.")
            continue

        codigos_excel = [c.strip() for c in str(codigo_excel).split(',')]
        soma_valores = soma_valores_correspondentes(df_csv, codigos_excel, co_excel, fonte_recurso_excel)

        if soma_valores > 0:
            valor_str = f"{soma_valores:.2f}".replace('.', ',')
            sheet.range(f'E{i}').value = valor_str
            st.write(f"Atualizado para {valor_str} na linha {i}.")
        else:
            st.write(f"Nenhuma correspondência encontrada para os códigos {codigo_excel} na linha {i}.")

   
    download_path = tempfile.mktemp(suffix='.xlsx')
    book.save(download_path)
    book.close()
    app.quit()

    
    return download_path

def main():
    st.title("Receita Corrente Líquida")
    
    csv_file = st.file_uploader("Carregar arquivo QGR", type=['csv'])
    excel_file = st.file_uploader("Carregar arquivo modelo Receita Corrente Líquida", type=['xlsx', 'xls'])

    if st.button("Processar Arquivos"):
        if csv_file and excel_file:
            download_path = processar_arquivos(csv_file, excel_file)
            with open(download_path, "rb") as file:
                st.download_button(
                        label="Baixar arquivo Excel processado",
                        data=file,
                        file_name="ReceitaCorrenteLiquida.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            os.remove(download_path)  
        else:
            st.error("Por favor, carregue ambos os arquivos antes de prosseguir.")

if __name__ == "__main__":
    main()
