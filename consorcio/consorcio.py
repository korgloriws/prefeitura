import streamlit as st
import pandas as pd
import io

colunas_selecionadas = [
    'CNPJ do Consórcio', 'Mês Referência', 'Código da função',
    'Código da subfunção', 'Natureza da despesa', 'Subelemento da despesa',
    'Código da fonte de recursos', 'Valor empenhado no mês',
    'Valor de empenhos anulados no mês', 'Valor liquidado no mês',
    'Valor de liquidações anuladas no mês', 'Valor pago no mês',
    'Valor de pagamentos anulados no mês'
]

def process_data(df):
    df['CNPJ do Consórcio'] = df['CNPJ do Consórcio'].astype(str).str.replace('.', '').str.zfill(14)

    df['Mês Referência'] = df['Mês Referência'].fillna(0).astype(int).astype(str).str.zfill(2)
    df['Natureza da despesa'] = df['Natureza da despesa'].astype(str).str.replace("'", "").str.slice(0, 6)
    df['Código da fonte de recursos'] = df['Código da fonte de recursos'].astype(str).str.replace('.0', '')

    cols_to_format = [
        'Código da função', 'Código da subfunção', 'Subelemento da despesa'
    ]

    for col in cols_to_format:
        df[col] = df[col].astype(str).str.replace("'", "")

    colunas_valor = [
        'Valor empenhado no mês', 'Valor de empenhos anulados no mês',
        'Valor liquidado no mês', 'Valor de liquidações anuladas no mês',
        'Valor pago no mês', 'Valor de pagamentos anulados no mês'
    ]

    for col in colunas_valor:
        df[col] = df[col].astype(float).map('{:,.2f}'.format).str.replace('.', '!').str.replace(',', '').str.replace('!', ',')

    df['cod. CO'] = ''
   
    col_order = [
        'CNPJ do Consórcio', 'Mês Referência', 'Código da função', 'Código da subfunção',
        'Natureza da despesa', 'Subelemento da despesa', 'Código da fonte de recursos',
        'cod. CO', 'Valor empenhado no mês', 'Valor de empenhos anulados no mês',
        'Valor liquidado no mês', 'Valor de liquidações anuladas no mês',
        'Valor pago no mês', 'Valor de pagamentos anulados no mês'
    ]
    df = df[col_order]

    return df


def main():
    st.title('Consórcio das Mulheres')

    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xls")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=0, usecols=colunas_selecionadas, dtype={'CNPJ do Consórcio': str})
        processed_df = process_data(df)

        st.write("Dados processados:")
        st.write(processed_df)

        file_name = st.text_input('Defina o nome do arquivo para download:', 'novo_arquivo.csv')

        csv_output = io.StringIO()
        processed_df.to_csv(csv_output, index=False, sep=';')  
        csv_output.seek(0)

        st.download_button(
            label="Baixar arquivo processado",
            data=csv_output.getvalue().encode('utf-8'),
            file_name=file_name,
            mime='text/csv'
        )


if __name__ == "__main__":
    main()