# Arquivo: streamlit_app.py

import streamlit as st
import pandas as pd

def converter_para_float(valor):
    if isinstance(valor, float):
        return valor
    try:
        return float(valor.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0


def processar_arquivo(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep=';', encoding='ISO-8859-1', on_bad_lines='skip')
        df['saldo_final'] = df['saldo_final'].apply(converter_para_float)
        df_filtrado = df[df['registro'] == 20]
        resultado = df_filtrado.groupby('fonte')['saldo_final'].sum()
        return resultado
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return None


def main():
    st.title("Somatório do CTB por orgãos")
    
    uploaded_file = st.file_uploader("Faça upload do arquivo CSV", type="csv")
    if uploaded_file is not None:
        resultado = processar_arquivo(uploaded_file)
        if resultado is not None:
            st.write(resultado)
            resultado.to_excel('resultado.xlsx')
            st.download_button(
                label="Baixar resultado em Excel",
                data=open('resultado.xlsx', 'rb'),
                file_name='resultado.xlsx',
                mime='application/vnd.ms-excel'
            )

if __name__ == "__main__":
    main()
