import pandas as pd
import streamlit as st
from io import BytesIO

def load_uploaded_file(uploaded_file):
    if uploaded_file:
        return pd.read_excel(uploaded_file, dtype=str)  
    return None

def main():
    st.title("Cismep")
    
    uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=['xlsx','xls'])
    
    if uploaded_file:
        data = load_uploaded_file(uploaded_file)
        column_name = 'NATUREZA DESPESA / SUBELEMENTO'

        if st.button('Filtrar e desmembrar coluna'):
            
            filtered_data = data[data[column_name].astype(str).str.replace('.', '').str.match(r'^\d{8}$')]
            filtered_data['NATUREZA DESPESA / SUBELEMENTO COM 6 DIGITOS'] = filtered_data[column_name].str.replace('.', '').str.slice(0, 6)
            filtered_data['NATUREZA DESPESA / SUBELEMENTO COM 2 DIGITOS'] = filtered_data[column_name].str.replace('.', '').str.slice(-2)

            
            filtered_data['CNPJ'] = filtered_data['CNPJ'].apply(lambda x: x.zfill(14))

           
            for col in ['Mês Referência', 'COD. FUNÇÃO']:
                if col in filtered_data.columns:
                    filtered_data[col] = filtered_data[col].apply(lambda x: x.zfill(2))

            
            filtered_data['CO'] = ''
            final_cols_order = ['CNPJ', 'Mês Referência', 'COD. FUNÇÃO', 'COD. SUBFUNÇÃO',
                                'NATUREZA DESPESA / SUBELEMENTO COM 6 DIGITOS', 
                                'NATUREZA DESPESA / SUBELEMENTO COM 2 DIGITOS',
                                'FONTE', 'CO',
                                'valor Empenhado no mês', 'Valor de empenhos anulados no mês',
                                'valor Liquidado no mês', 'Valor de liquidações anuladas no mês',
                                'Valor pago no mês', 'Valor de pagamentos anulados no mês']

            
            final_cols_order = [col for col in final_cols_order if col in filtered_data.columns]

            
            filtered_data = filtered_data[final_cols_order]

            
            value_cols = ['valor Empenhado no mês', 'Valor de empenhos anulados no mês', 'valor Liquidado no mês',
                          'Valor de liquidações anuladas no mês', 'Valor pago no mês', 'Valor de pagamentos anulados no mês']
            for col in value_cols:
                if col in filtered_data.columns:
                    filtered_data[col] = filtered_data[col].apply(lambda x: f"{float(x):,.2f}".replace('.', '|').replace(',', '').replace('|', ','))

           
            st.dataframe(filtered_data)

            
            csv = filtered_data.to_csv(index=False, sep=';')
            st.download_button(
                label='Clique para baixar o arquivo!',
                data=BytesIO(csv.encode()),
                file_name='dados_filtrados.csv',
                mime='text/csv'
            )
    else:
        st.write("Por favor, faça o upload de um arquivo Excel.")


if __name__ == "__main__":
    main()
