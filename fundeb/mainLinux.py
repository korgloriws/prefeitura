from openpyxl import load_workbook
import streamlit as st
import pandas as pd
from io import StringIO


def process_qgr(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
  
    df_filtrado = df[df['CODIGO_RECEITA'].isin([
        1751500100, 9217580111, 9817515001, 9917515001, 
        1321010100, 1922510100, 1922990100, 9819229901, 
        7922510100, 9819225101,9217515001
    ])]

    df_filtrado = df_filtrado[df_filtrado['FONTE_RECURSO'].isin([21540770, 21540000])]

    df_filtrado['VR_ARREC_ATE_MES_FONTE'] = (
        df_filtrado['VR_ARREC_ATE_MES_FONTE']
        .astype(str).str.strip()  
        .str.replace(r'[^\d,]', '', regex=True)  
        .str.replace(',', '.', regex=True) 
    )

    df_filtrado['VR_ARREC_ATE_MES_FONTE'] = pd.to_numeric(df_filtrado['VR_ARREC_ATE_MES_FONTE'], errors='coerce').fillna(0)

    return df_filtrado  


def process_ded(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
    
    df['fonte'] = df['fonte'].astype(str)
    df['liq_ate_mes'] = df['liq_ate_mes'].str.replace('.', '').str.replace(',', '.').astype(float)
    
 
 
    df_somente_21540770 = df[df['fonte'] == '21540770']
    soma_fonte_21540770 = df_somente_21540770['liq_ate_mes'].sum()



    df_filtrado = df[df['fonte'].isin(['21540770', '21540000'])]


    df_filtrado = df_filtrado[df_filtrado['programatica'].str.startswith('12.')]


    categorias_especificas = [
        "12.361", "12.362", "12.363", "12.364", "12.365", "12.366", "12.367"
    ]

    resultados = {}
    
    for categoria in categorias_especificas:
        resultados[categoria] = df_filtrado[df_filtrado['programatica'].str.startswith(categoria)]['liq_ate_mes'].sum()
    
    df_outros = df_filtrado[~df_filtrado['programatica'].str.startswith(tuple(categorias_especificas))]
    resultados["12.xxx"] = df_outros['liq_ate_mes'].sum()

 

    resultados["fonte_21540770"] = soma_fonte_21540770


    return resultados


def process_rpp_rpnp(file):
    df = pd.read_csv(file, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df_filtrado = df[df['fonte'].isin(['21540770', '21540000'])]
    resultado = df_filtrado['saldo_mes'].sum()
    return resultado


def fill_fundeb(file_path, qgr_data=None, ded_data=None, rpp_1619_data=None, rpnp_1619_data=None):
    workbook = load_workbook(filename=file_path)
    sheet = workbook.worksheets[1]  


    if qgr_data is not None:
        soma_qgr = qgr_data.groupby('CODIGO_RECEITA')['VR_ARREC_ATE_MES_FONTE'].sum().to_dict()

        for row in qgr_data.itertuples():
            if row.CODIGO_RECEITA == 1751500100:
                sheet['F8'].value = soma_qgr.get(1751500100, 0)
            elif row.CODIGO_RECEITA == 9217580111:
                sheet['F9'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 9817515001:
                sheet['F10'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 9917515001:
                sheet['F11'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 1321010100:
                sheet['F13'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 1922510100:
                sheet['F15'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 1922990100:
                sheet['F16'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 7922510100:
                sheet['F17'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 9819225101:
                sheet['F18'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 9217515001:
                sheet['F19'].value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == 9819229901:
                sheet['F20'].value = row.VR_ARREC_ATE_MES_FONTE

        soma_fonte = qgr_data['VR_ARREC_ATE_MES_FONTE'].sum()
        sheet['F46'].value = soma_fonte

    mapeamento_celulas = {
        "12.361": "F25",
        "12.362": "F26",
        "12.363": "F27",
        "12.364": "F28",
        "12.365": "F29",
        "12.366": "F30",
        "12.367": "F31",
        "12.xxx": "F32"
    }

    if ded_data is not None:
 
        for categoria, celula in mapeamento_celulas.items():
            sheet[celula].value = ded_data.get(categoria, 0)

   
        sheet['F41'].value = ded_data.get("fonte_21540770", 0)
   
    if rpp_1619_data is not None:
        sheet['F26'].value = rpp_1619_data  

    if rpnp_1619_data is not None:
        sheet['F27'].value = rpnp_1619_data 

    workbook.save(filename=file_path)
    workbook.close()


def main():
    st.title("FUNDEB")

    caminho_qgr = st.file_uploader("Carregue o arquivo QGR", type=['csv'])
    caminho_ded = st.file_uploader("Carregue o arquivo DED", type=['csv'])  
    caminho_rpp_1619 = st.file_uploader("Carregue o arquivo RPP 1619", type=['csv'])
    caminho_rpnp_1619 = st.file_uploader("Carregue o arquivo RPNP 1619", type=['csv'])
    caminho_fundeb = st.file_uploader("Carregue o arquivo FUNDEB", type=['xlsx'])

    if st.button('Processar Arquivos'):
        try:
            qgr_data = process_qgr(StringIO(caminho_qgr.getvalue().decode("latin1"))) if caminho_qgr else None
            ded_data = process_ded(StringIO(caminho_ded.getvalue().decode("latin1"))) if caminho_ded else None
            rpp_1619_data = process_rpp_rpnp(StringIO(caminho_rpp_1619.getvalue().decode("latin1"))) if caminho_rpp_1619 else None
            rpnp_1619_data = process_rpp_rpnp(StringIO(caminho_rpnp_1619.getvalue().decode("latin1"))) if caminho_rpnp_1619 else None

            if caminho_fundeb is not None:
                temp_file_path = "temp_FUNDEB.xlsx"
                with open(temp_file_path, "wb") as f:
                    f.write(caminho_fundeb.getbuffer())

                fill_fundeb(temp_file_path, qgr_data, ded_data, rpp_1619_data, rpnp_1619_data)

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
            st.error(f"Erro de decodificação: {e}. Verifique a codificação dos arquivos CSV.")


if __name__ == "__main__":
    main()
