import pandas as pd
import streamlit as st
from io import BytesIO

def limpar_valor_monetario(valor):

    if isinstance(valor, str):
        valor_limpo = valor.replace('.', '').replace(',', '.')
        return pd.to_numeric(valor_limpo, errors='coerce')
    return pd.to_numeric(valor, errors='coerce')

def main():
    st.title('Comparador de EMP')

    file_1149 = st.file_uploader("Escolha o arquivo 1149 CSV", type=['csv'])
    file_outro = st.file_uploader("Escolha o outro arquivo CSV", type=['csv'])

    if st.button('Comparar Arquivos'):
        if file_1149 and file_outro:
            df_1149 = pd.read_csv(file_1149, delimiter=';', encoding='ISO-8859-1', decimal=',')
            df_outro = pd.read_csv(file_outro, delimiter=';', encoding='ISO-8859-1', decimal=',')

            df_outro = df_outro[df_outro['registro'] == 10]

            df_outro['unidade_orcamentaria'] = df_outro['unidade_orcamentaria'].astype(str).str[-4:]
            df_outro['item_despesa'] = df_outro['item_despesa'].fillna(0).astype(int).apply(lambda x: f'{x:02d}')

            colunas_para_comparacao = ['num_emp', 'unidade_orcamentaria', 'natureza_despesa', 'item_despesa']

            for coluna in colunas_para_comparacao:
                df_1149[coluna] = pd.to_numeric(df_1149[coluna], errors='coerce').fillna(0)
                df_outro[coluna] = pd.to_numeric(df_outro[coluna], errors='coerce').fillna(0)

            
            df_1149['valor_emp'] = df_1149['valor_emp'].apply(limpar_valor_monetario).fillna(0).astype(float)
            df_outro['valor_emp'] = df_outro['valor_emp'].apply(limpar_valor_monetario).fillna(0).astype(float)

            comparacao_completa = df_1149.merge(df_outro, on=colunas_para_comparacao + ['valor_emp'], how='outer', indicator=True)
            diferencas = comparacao_completa[comparacao_completa['_merge'] != 'both']

            soma_1149 = df_1149['valor_emp'].sum()
            soma_outro = df_outro['valor_emp'].sum()

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                comparacao_completa[colunas_para_comparacao + ['valor_emp', '_merge']].to_excel(writer, index=False, sheet_name='Comparacao Completa')
                diferencas[colunas_para_comparacao + ['valor_emp', '_merge']].to_excel(writer, index=False, sheet_name='Diferencas Encontradas')
                pd.DataFrame({'Arquivo': ['1149', 'Outro'], 'Soma Valor Emp': [soma_1149, soma_outro]}).to_excel(writer, index=False, sheet_name='Soma Valor Emp')

            output.seek(0)

            st.download_button(
                label="Download do relatório de comparação em XLSX",
                data=output,
                file_name="relatorio_comparacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("Comparação concluída e relatório gerado com a soma dos valores.")
        else:
            st.error("Por favor, carregue ambos os arquivos CSV.")

if __name__ == "__main__":
    main()
