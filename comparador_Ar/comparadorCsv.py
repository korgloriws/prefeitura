import pandas as pd
import streamlit as st
import csv
import io
import base64

def brazilian_formatter(x):
    s = str(int(x))
    if len(s) <= 2:
        return f"0,{s.zfill(2)}"
    else:
        int_part = s[:-2]
        decimal_part = s[-2:]
        int_part_with_dot = f"{int(int_part):,}".replace(",", ".")
        return f"{int_part_with_dot},{decimal_part}"

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

def process_and_sum(df):
    totals = {}
   
    for bank in df['Text51'].unique():
        group = df[df['Text51'] == bank]
       
        if bank == 'Não Informado':
            group1 = group.iloc[:500]
            group2 = group.iloc[500:]
           
            totals['Banco 0'] = {
                'Descontos': round(group1['Text133'].sum(), 2),
                'Bruto': round(group1['Text134'].sum(), 2),
                'Liquido': round(group1['Text134'].sum() - group1['Text133'].sum(), 2)
            }
           
            totals['Banco 8888'] = {
                'Descontos': round(group2['Text133'].sum(), 2),
                'Bruto': round(group2['Text134'].sum(), 2),
                'Liquido': round(group2['Text134'].sum() - group2['Text133'].sum(), 2)
            }
        else:
            totals[bank] = {
                'Descontos': round(group['Text133'].sum(), 2),
                'Bruto': round(group['Text134'].sum(), 2),
                'Liquido': round(group['Text134'].sum() - group['Text133'].sum(), 2)
            }
   
    return totals



def run_app():
    st.title("Comparador AR")
   
    csv_file1 = st.file_uploader("com filtro", type=['csv'])
    csv_file2 = st.file_uploader("sem filtro", type=['csv'])
   
    if csv_file1 and csv_file2:
        df1 = read_and_locate_columns(csv_file1)
        df2 = read_and_locate_columns(csv_file2)
       
        if df1 is not None and df2 is not None:
            
            banks1 = set(df1['Text51'].unique())
            banks2 = set(df2['Text51'].unique())
           
           
            totals1 = process_and_sum(df1)
            totals2 = process_and_sum(df2)
           
            df_totals1 = pd.DataFrame.from_dict(totals1, orient='index')
            df_totals2 = pd.DataFrame.from_dict(totals2, orient='index')
           
            
            df_totals1_display = df_totals1.rename(columns={"Text133": "Descontos", "Text134": "Bruto", "Text135": "Líquido"})
            df_totals2_display = df_totals2.rename(columns={"Text133": "Descontos", "Text134": "Bruto", "Text135": "Líquido"})
           
           
           
            all_banks = list(set(df_totals1.index) | set(df_totals2.index))
            diff = pd.DataFrame(columns=df_totals1.columns, index=all_banks)

            for bank in all_banks:
                if bank in df_totals1.index and bank in df_totals2.index:
                    diff.loc[bank] = df_totals1.loc[bank] - df_totals2.loc[bank]
                elif bank in df_totals1.index:
                    diff.loc[bank] = df_totals1.loc[bank]
                elif bank in df_totals2.index:
                    diff.loc[bank] = -df_totals2.loc[bank]

            
            diff = diff[diff.abs().sum(axis=1) != 0]

           
            
            total_geral1 = df_totals1.sum()
            total_geral2 = df_totals2.sum()
           
            
            df_totals1_display = df_totals1_display.applymap(brazilian_formatter)
            df_totals2_display = df_totals2_display.applymap(brazilian_formatter)
            total_geral1 = total_geral1.map(brazilian_formatter)
            total_geral2 = total_geral2.map(brazilian_formatter)
            diff = diff.applymap(lambda x: brazilian_formatter(x) if isinstance(x, (int, float)) else x)
           
            
            st.write("Totais com filtro:")
            st.table(df_totals1_display)
            st.write("Totais sem filtro:")
            st.table(df_totals2_display)
            st.write("Total Geral com filtro:")
            st.write(total_geral1)
            st.write("Total Geral sem filtro:")
            st.write(total_geral2)
            st.write("Diferenças entre os totais:")
            st.table(diff)
           
            
            csv = diff.to_csv(index=True)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="diferencas.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    run_app()
