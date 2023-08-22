import streamlit as st
import pandas as pd
import io


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


def main():
    st.title('Organizador de tabela')

    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xls")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=1, usecols=colunas_selecionadas)
        processed_df = process_data(df)

        st.write("Dados processados:")
        st.write(processed_df)

        file_name = st.text_input('Defina o nome do arquivo para download:', 'novo_arquivo.csv')

        # Salvando o DataFrame processado em um objeto StringIO como .csv
        csv_output = io.StringIO()
        processed_df.to_csv(csv_output, index=False)
        csv_output.seek(0)  # volta para o começo do StringIO

        # Botão para baixar o arquivo .csv
        st.download_button(
            label="Baixar arquivo processado",
            data=csv_output.getvalue().encode('utf-8'),
            file_name=file_name,
            mime='text/csv'
        )

if __name__ == "__main__":
    main()


