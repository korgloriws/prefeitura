import streamlit as st
import pandas as pd
import xlwings as xw
from io import StringIO

def process_qgr(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
    filtro_192 = df['CODIGO_RECEITA'].astype(str).str.startswith('192')
    df_filtrado = df[filtro_192 | df['CODIGO_RECEITA'].isin([1751500100, 9217580111, 9817515001, 9917515001, 1321010100])]
    df_filtrado = df_filtrado[df_filtrado['FONTE_RECURSO'].isin([21540770, 21540000])]
    resultado = df_filtrado.groupby(['CODIGO_RECEITA', 'FONTE_RECURSO'])['VR_ARREC_ATE_MES_FONTE'].sum()
    return resultado.reset_index()

def process_ded(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df['liq_ate_mes'] = df['liq_ate_mes'].str.replace('.', '').str.replace(',', '.').astype(float)
    df_filtrado = df[df['fonte'].isin(['21540770', '21540000'])]
    resultado = df_filtrado['liq_ate_mes'].sum()
    return resultado

def process_rpp_rpnp(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df_filtrado = df[df['fonte'].isin(['21540770', '21540000'])]
    resultado = df_filtrado['saldo_mes'].sum()
    return resultado

def fill_fundeb(file_path, qgr_data=None, ded_361_data=None, ded_365_data=None, rpp_1619_data=None, rpnp_1619_data=None):
    app = xw.App(visible=True)
    workbook = app.books.open(file_path)
    sheet = workbook.sheets[1]  

    if qgr_data is not None:
        for row in qgr_data.itertuples():
            if row.CODIGO_RECEITA == 1751500100:
                sheet.range('F8').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 1321010100:
                sheet.range('F13').value = row.VR_ARREC_ATE_MES_FONTE
            elif str(row.CODIGO_RECEITA).startswith('192'):
                sheet.range('F15').value = row.VR_ARREC_ATE_MES_FONTE

    if ded_361_data is not None:
        sheet.range('F19').value = ded_361_data

    if ded_365_data is not None:
        sheet.range('F20').value = ded_365_data

    if rpp_1619_data is not None:
        sheet.range('F22').value = rpp_1619_data

    if rpnp_1619_data is not None:
        sheet.range('F23').value = rpnp_1619_data

    workbook.save()
    workbook.close()
    app.quit()

def main():
    st.title("FUNDEB")

    # Upload de arquivos
    caminho_qgr = st.file_uploader("Carregue o arquivo QGR", type=['csv'])
    caminho_ded_361 = st.file_uploader("Carregue o arquivo DED 361", type=['csv'])
    caminho_ded_365 = st.file_uploader("Carregue o arquivo DED 365", type=['csv'])
    caminho_rpp_1619 = st.file_uploader("Carregue o arquivo RPP 1619", type=['csv'])
    caminho_rpnp_1619 = st.file_uploader("Carregue o arquivo RPNP 1619", type=['csv'])
    caminho_fundeb = st.file_uploader("Carregue o arquivo FUNDEB", type=['xlsx'])

    # Botão para processar
    if st.button('Processar Arquivos'):
        try:
            qgr_data = process_qgr(StringIO(caminho_qgr.getvalue().decode("latin1"))) if caminho_qgr else None
            ded_361_data = process_ded(StringIO(caminho_ded_361.getvalue().decode("latin1"))) if caminho_ded_361 else None
            ded_365_data = process_ded(StringIO(caminho_ded_365.getvalue().decode("latin1"))) if caminho_ded_365 else None
            rpp_1619_data = process_rpp_rpnp(StringIO(caminho_rpp_1619.getvalue().decode("latin1"))) if caminho_rpp_1619 else None
            rpnp_1619_data = process_rpp_rpnp(StringIO(caminho_rpnp_1619.getvalue().decode("latin1"))) if caminho_rpnp_1619 else None

            
            if caminho_fundeb is not None:
                temp_file_path = "temp_FUNDEB.xlsx"
                with open(temp_file_path, "wb") as f:
                    f.write(caminho_fundeb.getbuffer())
                fill_fundeb(temp_file_path, qgr_data, ded_361_data, ded_365_data, rpp_1619_data, rpnp_1619_data)
                
                
                with open(temp_file_path, "rb") as f:
                    st.download_button(
                        label="Baixar arquivo FUNDEB processado",
                        data=f,
                        file_name="FUNDEB_processado.xlsx",
                        mime="application/vnd.ms-excel"
                    )

                st.success("Processamento concluído! Você pode baixar o arquivo FUNDEB preenchido abaixo.")
            else:
                st.error("Por favor, carregue o arquivo FUNDEB.")
        except UnicodeDecodeError as e:
            st.error(f"Erro de decodificação: {e}. Por favor, verifique a codificação dos arquivos CSV.")

if __name__ == "__main__":
    main()
