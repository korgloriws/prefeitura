import pandas as pd
import xlwings as xw

def process_qgr(file_path):
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
    df['CODIGO_RECEITA'] = df['CODIGO_RECEITA'].astype(str)
    df['VR_ARREC_ATE_MES_FONTE'] = df['VR_ARREC_ATE_MES_FONTE'].str.replace('.', '').str.replace(',', '.').astype(float)
    resultado = df.groupby('CODIGO_RECEITA')['VR_ARREC_ATE_MES_FONTE'].sum()
    return resultado.reset_index()

def process_ded(file_path):
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df['liq_ate_mes'] = df['liq_ate_mes'].str.replace('.', '').str.replace(',', '.').astype(float)
    fontes_especificas = ['1500702', '2500702', '31500702', '51500702']
    df_filtrado = df[df['fonte'].isin(fontes_especificas)]
    resultado = df_filtrado['liq_ate_mes'].sum()
    return resultado

def fill_demostrativo_saude(file_path, qgr_data=None, ded_data=None):
    app = xw.App(visible=True)
    workbook = app.books.open(file_path)
    sheet = workbook.sheets[1]

    soma_valores_especificos = 0

    if qgr_data is not None:
        for row in qgr_data.itertuples():
            if row.CODIGO_RECEITA == '1112500100':
                sheet.range('G8').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112530100':
                sheet.range('G9').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1113031100':
                sheet.range('G10').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1113034100':
                sheet.range('G11').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1114511100':
                sheet.range('G12').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1711511100':
                sheet.range('G17').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1711520100':
                sheet.range('G18').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1721500100':
                sheet.range('G19').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1721510100':
                sheet.range('G20').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1721520100':
                sheet.range('G21').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1115010000':
                sheet.range('G22').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112500200':
                sheet.range('G28').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112500300':
                sheet.range('G29').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112500400':
                sheet.range('G30').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112530200':
                sheet.range('G31').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112530300':
                sheet.range('G32').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1112530400':
                sheet.range('G33').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1114511200':
                sheet.range('G34').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1114511300':
                sheet.range('G35').value = row.VR_ARREC_ATE_MES_FONTE
            elif row.CODIGO_RECEITA == '1114511400':
                sheet.range('G36').value = row.VR_ARREC_ATE_MES_FONTE

            elif row.CODIGO_RECEITA in ['1114511400', '9111125001', '9111125002', '9111125003', 
                                       '9111125004', '9111125301', '9111145111', '9111145112', 
                                       '9111145113', '9111145114', '9211125001', '9211125002', 
                                       '9211125003', '9211125004', '9211125301', '9211130341', 
                                       '9211145111', '9211145112', '9311125001', '9311125002', 
                                       '9311125003', '9311125004', '9311125301', '9311125302', 
                                       '9311145111', '9311145112', '9311145113', '9311145114', 
                                       '9111145111']:
                if row.VR_ARREC_ATE_MES_FONTE != 0:
                    soma_valores_especificos += row.VR_ARREC_ATE_MES_FONTE

    sheet.range('G39').value = soma_valores_especificos

    if ded_data is not None:
        sheet.range('G42').value = ded_data

    workbook.save()
    workbook.close()
    app.quit()

caminho_qgr = '966_QGR.csv'
caminho_ded = '938_DED.csv'
caminho_demostrativo_saude = 'DEMONSTRATIVO SAÚDE.xlsx'

qgr_data = process_qgr(caminho_qgr) if caminho_qgr else None
ded_data = process_ded(caminho_ded) if caminho_ded else None

fill_demostrativo_saude(caminho_demostrativo_saude, qgr_data, ded_data)
