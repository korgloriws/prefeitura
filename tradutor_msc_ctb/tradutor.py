import pandas as pd
import streamlit as st
from io import BytesIO


def traduzir_contas(msc_df, contas_aplicacao_df):
    st.write("Iniciando a tradução das contas contábeis...")


    conta_mapping = dict(zip(contas_aplicacao_df['cod_contabil'], contas_aplicacao_df['cod_reduz']))

  
    msc_df['CONTA'] = msc_df['CONTA'].map(conta_mapping)


    msc_traduzido = msc_df[msc_df['CONTA'].notna()]

    st.write(f"Tradução concluída. Registros traduzidos: {len(msc_traduzido)}")
    
    return msc_traduzido


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data


def main():
    st.title("Corretor da Matriz para o CTB")


    msc_file = st.file_uploader("Carregar o arquivo MSC", type=["xlsx"])
    contas_aplicacao_file = st.file_uploader("Carregar o arquivo Instituições financeiras 993", type=["xlsx"])

    if msc_file and contas_aplicacao_file:

        msc_df = pd.read_excel(msc_file)
        contas_aplicacao_df = pd.read_excel(contas_aplicacao_file)

        msc_traduzido = traduzir_contas(msc_df, contas_aplicacao_df)


        excel_data = to_excel(msc_traduzido)


        st.success("Tradução concluída com sucesso!")
        st.download_button(label="Baixar MSC Traduzida", data=excel_data, file_name="MSC_Traduzido.xlsx")

if __name__ == '__main__':
    main()
