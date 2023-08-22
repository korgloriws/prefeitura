import pandas as pd
import streamlit as st

def compara_dados(df1, df2):
    erros_cod_contabil = []
    erros_valores = []

    for index, row in df1.iterrows():
        df2_row = df2[df2['cod_contabil'] == row['cod_contabil']]

        if df2_row.empty:
            print(f"Erro: cod_contabil {row['cod_contabil']} não encontrado em df2")
            erros_cod_contabil.append({
                'cod_contabil': row['cod_contabil'],
                'debito_anterior1': row['debito_anterior'],
                'credito_anterior1': row['credito_anterior'],
                'debito_mes1': row['debito_mes'],
                'credito_mes1': row['credito_mes'],
                'debito_atual1': row['debito_atual'],
                'credito_atual1': row['credito_atual'],
                'debito_anterior2': "N/A",
                'credito_anterior2': "N/A",
                'debito_mes2': "N/A",
                'credito_mes2': "N/A",
                'debito_atual2': "N/A",
                'credito_atual2': "N/A",
            })
        else:
            df2_row = df2_row.iloc[0]
            if (row['debito_anterior'] != df2_row['debito_anterior'] or
                row['credito_anterior'] != df2_row['credito_anterior'] or
                row['debito_mes'] != df2_row['debito_mes'] or
                row['credito_mes'] != df2_row['credito_mes'] or
                row['debito_atual'] != df2_row['debito_atual'] or
                row['credito_atual'] != df2_row['credito_atual']):
                print(f"Erro: Valores não batem para cod_contabil {row['cod_contabil']}")
                erros_valores.append({
                    'cod_contabil': row['cod_contabil'],
                    'debito_anterior1': row['debito_anterior'],
                    'credito_anterior1': row['credito_anterior'],
                    'debito_mes1': row['debito_mes'],
                    'credito_mes1': row['credito_mes'],
                    'debito_atual1': row['debito_atual'],
                    'credito_atual1': row['credito_atual'],
                    'debito_anterior2': df2_row['debito_anterior'],
                    'credito_anterior2': df2_row['credito_anterior'],
                    'debito_mes2': df2_row['debito_mes'],
                    'credito_mes2': df2_row['credito_mes'],
                    'debito_atual2': df2_row['debito_atual'],
                    'credito_atual2': df2_row['credito_atual'],
                })
    return erros_cod_contabil, erros_valores

st.title('Camara VS Sicof')

arquivo1 = st.file_uploader("Arquivo Câmara", type=['csv'])
arquivo2 = st.file_uploader("Arquivo Sicof", type=['csv'])

if arquivo1 and arquivo2:
    df1 = pd.read_csv(arquivo1, encoding='ISO-8859-1', sep=';')
    df2 = pd.read_csv(arquivo2, encoding='ISO-8859-1', sep=';')

    if df1.columns.tolist() == df2.columns.tolist():
        erros_cod_contabil, erros_valores = compara_dados(df1, df2)

        if erros_cod_contabil or erros_valores:
            if erros_cod_contabil:
                df_erros_cod_contabil = pd.DataFrame(erros_cod_contabil)
                st.write("Erros onde o cod_contabil não foi encontrado:")
                st.table(df_erros_cod_contabil)

            if erros_valores:
                df_erros_valores = pd.DataFrame(erros_valores)
                st.write("Erros onde os valores não batem:")
                st.table(df_erros_valores)

            nome_arquivo = st.text_input("Nome do arquivo para download", "erros.csv")

            if st.button('Baixar Arquivo'):
                st.download_button(
                    label="Baixar erros",
                    data=pd.concat([df_erros_cod_contabil, df_erros_valores]).to_csv(index=False),
                    file_name=nome_arquivo,
                    mime="text/csv"
                )
        else:
            st.success('Não foram encontradas diferenças.')
    else:
        st.error('Os arquivos não têm o mesmo formato.')

def main():  # Esta é a nova função main.
    st.title('Camara VS Sicof')

    arquivo1 = st.file_uploader("Arquivo Câmara", type=['csv'])
    arquivo2 = st.file_uploader("Arquivo Sicof", type=['csv'])

    if arquivo1 and arquivo2:
        df1 = pd.read_csv(arquivo1, encoding='ISO-8859-1', sep=';')
        df2 = pd.read_csv(arquivo2, encoding='ISO-8859-1', sep=';')

        if df1.columns.tolist() == df2.columns.tolist():
            erros_cod_contabil, erros_valores = compara_dados(df1, df2)

            if erros_cod_contabil or erros_valores:
                if erros_cod_contabil:
                    df_erros_cod_contabil = pd.DataFrame(erros_cod_contabil)
                    st.write("Erros onde o cod_contabil não foi encontrado:")
                    st.table(df_erros_cod_contabil)

                if erros_valores:
                    df_erros_valores = pd.DataFrame(erros_valores)
                    st.write("Erros onde os valores não batem:")
                    st.table(df_erros_valores)

                nome_arquivo = st.text_input("Nome do arquivo para download", "erros.csv")

                if st.button('Baixar Arquivo'):
                    st.download_button(
                        label="Baixar erros",
                        data=pd.concat([df_erros_cod_contabil, df_erros_valores]).to_csv(index=False),
                        file_name=nome_arquivo,
                        mime="text/csv"
                    )
            else:
                st.success('Não foram encontradas diferenças.')
        else:
            st.error('Os arquivos não têm o mesmo formato.')

if __name__ == "__main__":
    main()