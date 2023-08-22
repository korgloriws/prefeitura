import re
import locale
import pandas as pd
import datetime
import pdfplumber
import streamlit as st
import base64
import io

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def process_pdf(file):
    sum_resgate = 0
    sum_aplicacao = 0
    sum_rendimento = 0
    sum_estorno_de_re = 0

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                line = re.sub(r'\s+', ' ', line)

                if re.search(r'resgate,', line, re.IGNORECASE):
                    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', line)
                    if match:
                        valor = locale.atof(match.group(1))
                        sum_resgate += valor

                if re.search(r'aplicacao', line, re.IGNORECASE):
                    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', line)
                    if match:
                        valor = locale.atof(match.group(1))
                        sum_aplicacao += valor

                if re.search(r'rendimento', line, re.IGNORECASE):
                    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', line)
                    if match:
                        valor = locale.atof(match.group(1))
                        sum_rendimento += valor

                if re.search(r'estorno de re', line, re.IGNORECASE):
                    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', line)
                    if match:
                        valor = locale.atof(match.group(1))
                        sum_estorno_de_re += valor

    data = {
        'Tipo': ['Resgate', 'Aplicacao', 'Rendimento', 'Estorno de RE'],
        'Total': [sum_resgate, sum_aplicacao, sum_rendimento, sum_estorno_de_re]
    }
    df = pd.DataFrame(data)
    df['Total'] = df['Total'].apply(lambda x: locale.currency(x, grouping=True))
    return df

def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_column('B:B', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename):
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.xlsx">Download Excel file</a>'

def main():
    st.title('Precatórios')

    file = st.file_uploader('Carregar arquivo PDF', type=['pdf'])
    if file is not None:
        filename = st.text_input("Digite o nome do arquivo para salvar: ")
        df = process_pdf(file)
        if st.button('Processar'):
            if filename != "":
                date_str = datetime.datetime.now().strftime("%d/%m/%Y")
                st.markdown(f"**Nome do arquivo:** {filename}")
                st.markdown(f"**Data de geração:** {date_str}")
                st.write(df)
                st.success(f'Arquivo gerado com sucesso: {filename}')
                
                # Convertendo DataFrame para Excel
                excel_data = to_excel(df)

                # Criando botão de download
                st.download_button(
                    label="Download Excel file",
                    data=excel_data,
                    file_name=f"{filename}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.error("Por favor, insira um nome para o arquivo antes de processar.")


if __name__ == '__main__':
    main()
