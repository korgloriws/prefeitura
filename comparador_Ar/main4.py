import pandas as pd
import streamlit as st
import csv
import io

def format_value(value):
    
    number = float(value)
    formatted_value = "{:,.2f}".format(number).replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted_value

def read_total_liquido_geral(file, col_correct, key):
    text_data = file.read().decode('ISO-8859-1')
    text_file = io.StringIO(text_data)
    df = pd.read_csv(text_file, delimiter=';', header=None)
    row_index = df[df[0].str.contains('Total Líquido Geral:', case=False, na=False)].index[0]
    col_index = 17  
    
    if col_correct == 'Não':
        col_index = st.number_input("Insira o número da coluna correta (começando em 0):", min_value=0, value=17, step=1, key=f"number_{key}")
    
    value = df.iloc[row_index, col_index]
    if isinstance(value, str):
        value = value.strip().replace('.', '').replace(',', '.')
    else:
        value = str(value).replace('.', '').replace(',', '.')
    
    return float(value)

def get_cp_value(file, col_correct):
    text_data = file.read().decode('ISO-8859-1')
    text_file = io.StringIO(text_data)
    df = pd.read_csv(text_file, delimiter=';', header=None)
    row_index = df[df[1].str.contains('Total Geral', case=False, na=False)].index[0]
    col_index = 16 
    if col_correct == 'Não':
        col_index = st.number_input("Insira o número da coluna correta para o CP (começando em 0):", min_value=0, value=16, step=1)
    value = df.iloc[row_index, col_index].strip()
    return float(value.replace('.', '').replace(',', '.')) if isinstance(value, str) else value

def main():
    st.title("Comparador AR")
    csv_file1 = st.file_uploader("Por lote", type=['csv'])
    csv_file2 = st.file_uploader("Por Banco", type=['csv'])
    cp_file = st.file_uploader("CP", type=['csv'])

    if csv_file1 and csv_file2 and cp_file:
        with st.expander("Verificar Colunas dos Arquivos"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("A coluna com o valor de 'Total Líquido Geral' está correta? (Arquivo Por lote)")
                col_correct1 = st.radio("", ('Sim', 'Não'), key='radio1')
            with col2:
                st.write("A coluna com o valor de 'Total Líquido Geral' está correta? (Arquivo Por Banco)")
                col_correct2 = st.radio("", ('Sim', 'Não'), key='radio2')
            with col3:
                st.write("A coluna com o valor do CP está correta? (Padrão: Coluna 16)")
                col_correct_cp = st.radio("", ('Sim', 'Não'), key='cp')

        total_liquido1 = read_total_liquido_geral(csv_file1, col_correct1, 'radio1')
        total_liquido2 = read_total_liquido_geral(csv_file2, col_correct2, 'radio2')
        cp_value = get_cp_value(cp_file, col_correct_cp)

        if total_liquido1 is not None and total_liquido2 is not None:
            data = {
                'Descrição': ['Total Geral Por lote (líquido)', 'Total Geral Por Banco (líquido)', 'Valor do arquivo CP'],
                'Valor': [format_value(total_liquido1), format_value(total_liquido2), format_value(cp_value)]
            }
            df_display = pd.DataFrame(data)
            st.table(df_display)

if __name__ == '__main__':
    main()

