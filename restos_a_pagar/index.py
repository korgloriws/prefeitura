import pandas as pd
import streamlit as st
from io import BytesIO

def padronizar_dataframe(df, numeric_columns):
    df.fillna(0, inplace=True)
    for col in numeric_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.')
            try:
                df[col] = df[col].astype(float).round(2)
            except ValueError:
                st.warning(f"Não foi possível converter a coluna {col} para float.")
    return df

def compara_dados(df1, df2, columns_to_compare):
    erros = []
    for index, row in df1.iterrows():
        df2_row = df2[df2['num_emp'] == row['num_emp']]
        
        if df2_row.empty:
            erros.append({'num_emp': row['num_emp'], 'Erro': 'Não encontrado no segundo DataFrame', 'Valor_DF1': 'N/A', 'Valor_DF2': 'N/A'})
        else:
            df2_row = df2_row.iloc[0]
            for col in columns_to_compare:
                if row[col] != df2_row[col]:
                    erros.append({
                        'num_emp': row['num_emp'],
                        'Coluna': col,
                        'Valor_DF1': row[col],
                        'Valor_DF2': df2_row[col]
                    })
    return erros

def main():
    st.title('Restos a pagar camara VS sicof')
    
    arquivo1 = st.file_uploader("Restos a pagar camara", type=['csv'])
    arquivo2 = st.file_uploader("Restos a pagar sicof", type=['csv'])
    
    if arquivo1 and arquivo2:
        df1 = pd.read_csv(arquivo1, encoding='ISO-8859-1', sep=';')
        df2 = pd.read_csv(arquivo2, encoding='ISO-8859-1', sep=';')
        
        columns_to_compare = [
            "num_emp",   "fonte",  "valor",
            "valor_anu_ant", "valor_anu_mes", "valor_em_liq_ant", "valor_em_liq_mes",
            "valor_liq_ant", "valor_liq_mes", "valor_pag_ant", "valor_pag_mes",
            "saldo_ant", "saldo_mes"
        ]
    
        df1 = padronizar_dataframe(df1, columns_to_compare)
        df2 = padronizar_dataframe(df2, columns_to_compare)
    
        erros = compara_dados(df1, df2, columns_to_compare)
        
        if erros:
            df_erros = pd.DataFrame(erros)
            st.write("Erros encontrados:")
            st.table(df_erros)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_erros.to_excel(writer, sheet_name='Erros', index=False)
            
            output.seek(0)
            
            file_name = st.text_input("Nome do arquivo Excel:", value='erros_comparacao.xlsx')
            
            st.download_button(
                label="Baixar arquivo com erros",
                data=output,
                file_name=file_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        else:
            st.success('Não foram encontradas diferenças.')

if __name__ == '__main__':
    main()
