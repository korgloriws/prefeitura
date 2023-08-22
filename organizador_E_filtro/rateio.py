import pandas as pd
import streamlit as st
from io import BytesIO

def load_uploaded_file(uploaded_file):
    if uploaded_file:
        return pd.read_excel(uploaded_file)
    return None

st.title("Filtrador e Manipulador de Tabela")

uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=['xlsx'])

if uploaded_file:
    data = load_uploaded_file(uploaded_file)
    column_name = 'NATUREZA DESPESA / SUBELEMENTO'

    if st.button('Filtrar e desmembrar coluna'):
        # Filtrando por 8 dígitos e removendo os pontos
        filtered_data = data[data[column_name].astype(str).str.replace('.', '').str.match(r'^\d{8}$')]

        # Criando as novas colunas com base nos 6 primeiros e 2 últimos dígitos
        filtered_data['NATUREZA DESPESA / SUBELEMENTO COM 6 DIGITOS'] = filtered_data[column_name].str.replace('.', '').str.slice(0, 6)
        filtered_data['NATUREZA DESPESA / SUBELEMENTO COM 2 DIGITOS'] = filtered_data[column_name].str.replace('.', '').str.slice(-2)

        st.write(f'Dados filtrados e desmembrados da coluna "{column_name}":')
        st.dataframe(filtered_data)

        # Gerando o arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_data.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label='Clique para baixar o arquivo!',
            data=output,
            file_name='dados_filtrados.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.write("Por favor, faça o upload de um arquivo Excel.")
