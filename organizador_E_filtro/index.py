import streamlit as st
import pandas as pd
import io
from io import BytesIO

def func_one():
    colunas_selecionadas = ['CNPJ do Consórcio', 'Mês Referência', 'Código da função', 'Código da subfunção',
                            'Natureza da despesa', 'Subelemento da despesa', 'Código da fonte de recursos',
                            'Valor empenhado no mês', 'Valor de empenhos anulados no mês',
                            'Valor liquidado no mês', 'Valor de liquidações anuladas no mês',
                            'Valor pago no mês', 'Valor de pagamentos anulados no mês']

    def process_data(df):
        df['CNPJ do Consórcio'] = df['CNPJ do Consórcio'].astype(str).str.split(".").str[0].str.zfill(14)
        df['Mês Referência'] = df['Mês Referência'].fillna(0).astype(int).astype(str).str.zfill(2)
        cols_to_format = {
            'Código da função': 2,
            'Código da subfunção': 3,
            'Natureza da despesa': 6,
            'Subelemento da despesa': 2,
            'Código da fonte de recursos': 7,
        }
        for col, digits in cols_to_format.items():
            df[col] = df[col].astype(str).str.replace("'", "")
            df[col] = df[col].str.zfill(digits)
        colunas_valor = [
            'Valor empenhado no mês', 'Valor de empenhos anulados no mês',
            'Valor liquidado no mês', 'Valor de liquidações anuladas no mês',
            'Valor pago no mês', 'Valor de pagamentos anulados no mês'
        ]
        for col in colunas_valor:
            df[col] = df[col].apply(lambda x: float(str(x).replace(',', '').replace('.', '').strip()) / 100 if isinstance(x, str) else x)
            df[col] = df[col].apply(lambda x: '{:,.2f}'.format(x).replace('.', '!').replace(',', '').replace('!', ','))
        return df

    uploaded_file = st.file_uploader("Escolha um arquivo Excel (Organizador de tabela)", type="xls")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=1, usecols=colunas_selecionadas)
        processed_df = process_data(df)

        st.write("Dados processados:")
        st.write(processed_df)

        file_name = st.text_input('Defina o nome do arquivo para download:', 'novo_arquivo.xlsx')

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, sheet_name='Sheet1', index=False)
        output.seek(0)

        st.download_button(
            label="Baixar arquivo processado",
            data=output,
            file_name=file_name,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

def func_two():
    def load_uploaded_file(uploaded_file):
        if uploaded_file:
            return pd.read_excel(uploaded_file)
        return None

    uploaded_file = st.file_uploader("Selecione um arquivo Excel (Filtrador e Manipulador de Tabela)", type=['xlsx'])

    if uploaded_file:
        data = load_uploaded_file(uploaded_file)
        column_name = 'NATUREZA DESPESA / SUBELEMENTO'
        
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

st.sidebar.title("Selecione a Função")
option = st.sidebar.selectbox("Escolha a funcionalidade", ["organizador", "filtro"])

def main():
    st.sidebar.title("Selecione a Função")
    option = st.sidebar.selectbox("Escolha a funcionalidade", ["organizador", "filtro"])

    if option == "organizador":
        func_one()
    elif option == "filtro":
        func_two()


if __name__ == "__main__":
    main()