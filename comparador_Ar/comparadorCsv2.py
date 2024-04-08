import pandas as pd
import streamlit as st
import csv
import io



def format_value(value):
    
    if isinstance(value, str):
        value = value.replace('.', '').replace(',', '.')
    number = float(value) / 100 

    
    formatted_value = "{:,.2f}".format(number).replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted_value


def read_and_locate_columns(file):
    rows = []
    text_data = file.read().decode('ISO-8859-1')
    text_file = io.StringIO(text_data)
   
    csv_reader = csv.reader(text_file, delimiter=';')
    for row in csv_reader:
        rows.append(row)
       
    df = pd.DataFrame(rows[1:], columns=rows[0])
   
    if all(col in df.columns for col in ['Text51', 'Text133', 'Text134']):
        for col in ['Text133', 'Text134']:
            df[col] = df[col].str.replace(',', '.').str.replace('.', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
       
        df.dropna(subset=['Text133', 'Text134'], inplace=True)
       
        return df
    else:
        st.write("Colunas necessárias não encontradas.")
        return None
def process_and_sum_liquido(df):
    totals = df.groupby('Text51').apply(lambda x: (x['Text134'] - x['Text133']).sum()).sum()
    return int(totals)  


def get_cp_value(file):
    text_data = file.read().decode('ISO-8859-1')
    text_file = io.StringIO(text_data)
    df = pd.read_csv(text_file, header=None, delimiter=';')
    row_index = df[df[1] == 'Total Geral'].index[0] 

   
    col_index = 15  
    col_correct = st.radio("A coluna com o valor do CP está correta? (Padrão: Coluna 15)", ('Sim', 'Não'))

    if col_correct == 'Não':
        col_index = st.number_input("Insira o número da coluna correta (começando em 0):", min_value=0, value=15, step=1)

    value = df.iloc[row_index, col_index].strip() 
    return value



def calculate_differences(total1, total2, cp_value):
    
    total1_float = total1 / 100.0
    total2_float = total2 / 100.0
    cp_value_float = cp_value / 100.0

    
    diff1 = total1_float - cp_value_float
    diff2 = total2_float - cp_value_float
    return diff1, diff2


def main():
    st.title("Comparador AR")

    csv_file1 = st.file_uploader("Por lote", type=['csv'])
    csv_file2 = st.file_uploader("Por Banco", type=['csv'])
    cp_file = st.file_uploader("CP", type=['csv'])

    if csv_file1 and csv_file2 and cp_file:
        df1 = read_and_locate_columns(csv_file1)
        df2 = read_and_locate_columns(csv_file2)
        cp_value = get_cp_value(cp_file)

        if df1 is not None and df2 is not None:
            total_liquido1 = process_and_sum_liquido(df1)
            total_liquido2 = process_and_sum_liquido(df2)

          
            data = {
                'Descrição': ['Total Geral Por lote  (líquido)', 'Total Geral Por Banco (líquido)', 'Valor do arquivo CP'],
                'Valor': [format_value(total_liquido1), format_value(total_liquido2), cp_value]
            }
            df_display = pd.DataFrame(data)
            st.table(df_display)

          

if __name__ == '__main__':
   main()

