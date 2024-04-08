import pandas as pd
import xlwings as xw

def process_qgr(file_path):
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
    df['CODIGO_RECEITA'] = df['CODIGO_RECEITA'].astype(str)
    df['FONTE_RECURSO'] = df['FONTE_RECURSO'].apply(lambda x: str(int(float(x))) if pd.notna(x) else x)
    df['VR_ARREC_ATE_MES_FONTE'] = df['VR_ARREC_ATE_MES_FONTE'].str.replace('.', '').str.replace(',', '.').astype(float)
    resultado = df.groupby(['CODIGO_RECEITA', 'FONTE_RECURSO'])['VR_ARREC_ATE_MES_FONTE'].sum().reset_index()
    return resultado


def process_ded(file_path):
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df['liq_ate_mes'] = df['liq_ate_mes'].str.replace('.', '').str.replace(',', '.').astype(float)
    fontes_especificas = ['1500701', '2500701', '31500701', '51500701' , '2500701', '21540770']
    df_filtrado = df[df['fonte'].isin(fontes_especificas)]
    resultado = df_filtrado.groupby('fonte')['liq_ate_mes'].sum()
    return resultado.reset_index()

def process_rpnp(file_path):
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
    df['fonte'] = df['fonte'].astype(str)
    df['valor_anu_ant'] = df['valor_anu_ant'].str.replace('.', '').str.replace(',', '.').astype(float)
    fontes_especificas = ['1500701', '31500701', '51500701', '2500701', '32500701', '52500701']
    df_filtrado = df[df['fonte'].isin(fontes_especificas)]
    resultado = df_filtrado.groupby('fonte')['valor_anu_ant'].sum()
    return resultado.reset_index()

def fill_MDE(file_path, qgr_data=None, ded_data=None, rpnp_data=None):
    app = xw.App(visible=True)
    workbook = app.books.open(file_path)
    sheet = workbook.sheets[1]

   
    soma_valores_G56 = 0
    soma_valores_G57 = 0
    soma_valores_G58 = 0
    soma_valores_G59 = 0
    soma_valores_G61 = 0
    soma_valores_especificos = 0

    if qgr_data is not None:
        for row in qgr_data.itertuples():
            
            if row.CODIGO_RECEITA in ['1112500100']: 
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G9').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112530100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G10').value = soma_valores  
            if row.CODIGO_RECEITA in ['1113031100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G11').value = soma_valores  
            if row.CODIGO_RECEITA in ['1113034100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G12').value = soma_valores  
            if row.CODIGO_RECEITA in ['1114511100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G13').value = soma_valores  
            if row.CODIGO_RECEITA in ['1711511100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G18').value = soma_valores  
            if row.CODIGO_RECEITA in ['1711513100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G19').value = soma_valores  
            if row.CODIGO_RECEITA in ['1711512100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G20').value = soma_valores  
            if row.CODIGO_RECEITA in ['1711520100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G21').value = soma_valores  
            if row.CODIGO_RECEITA in ['1719610100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G22').value = soma_valores  
            if row.CODIGO_RECEITA in ['1721500100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G23').value = soma_valores  
            if row.CODIGO_RECEITA in ['1721510100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G24').value = soma_valores  
            if row.CODIGO_RECEITA in ['1721520100']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G25').value = soma_valores  
            if row.CODIGO_RECEITA in ['1115010000']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G26').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112500200']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G32').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112500300']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G33').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112500400']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G34').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112530200']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G35').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112530300']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G36').value = soma_valores  
            if row.CODIGO_RECEITA in ['1112530400']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G37').value = soma_valores  
            if row.CODIGO_RECEITA in ['1114511200']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G38').value = soma_valores  
            if row.CODIGO_RECEITA in ['1114511300']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G39').value = soma_valores  
            if row.CODIGO_RECEITA in ['1114511400']:  
                soma_valores = qgr_data[(qgr_data['CODIGO_RECEITA'] == row.CODIGO_RECEITA)]['VR_ARREC_ATE_MES_FONTE'].sum()
                sheet.range('G40').value = soma_valores  

           
            elif row.CODIGO_RECEITA in ['9111125001', '9111125002', '9111125003', '9111125004', '9111125301', '9111145111', '9111145112', '9111145113', '9111145114', '9211125001', '9211125002', '9211125003', '9211125004', '9211125301', '9211130341', '9211145111', '9211145112', '9311125001', '9311125002', '9311125003', '9311125004', '9311125301', '9311125302', '9311145111', '9311145112', '9311145113', '9311145114', '9111145111','9111145131','9111145121', '9517196101']:
                soma_valores_especificos += row.VR_ARREC_ATE_MES_FONTE

            elif row.CODIGO_RECEITA in ['9500000000', '9517115111', '9517115201', '9517215001', '9517215101', '9517215201']:
                soma_valores_G56 += row.VR_ARREC_ATE_MES_FONTE

            elif row.CODIGO_RECEITA in ['1751000000', '1751500000', '1751500100', '1751500100']:
                soma_valores_G57 += row.VR_ARREC_ATE_MES_FONTE   

            if row.CODIGO_RECEITA == '1321010100':
                
                if row.FONTE_RECURSO in ['21540770', '21540000', '31500701', '51500701']:
                    soma_valores_G58 += row.VR_ARREC_ATE_MES_FONTE
                   

            if row.CODIGO_RECEITA == '1922990100':
                
                if row.FONTE_RECURSO in ['21540770', '21540000', '31500701', '51500701']:
                    soma_valores_G59 += row.VR_ARREC_ATE_MES_FONTE
                    

        sheet.range('G56').value = soma_valores_G56
        sheet.range('G57').value = soma_valores_G57
        sheet.range('G58').value = soma_valores_G58
        sheet.range('G59').value = soma_valores_G59
        sheet.range('G43').value = soma_valores_especificos

    

    
    if ded_data is not None:
        for row in ded_data.itertuples():
            if row.fonte == '1500701':
                sheet.range('G49').value = row.liq_ate_mes
            if row.fonte == '31500701':
                sheet.range('G50').value = row.liq_ate_mes
            if row.fonte == '51500701':
                sheet.range('G51').value = row.liq_ate_mes
            if row.fonte == '2500701':
                sheet.range('G52').value = row.liq_ate_mes
            if row.fonte == '32500701':
                sheet.range('G53').value = row.liq_ate_mes
            if row.fonte == '52500701':
                sheet.range('G54').value = row.liq_ate_mes
            elif row.fonte in ['21540770', '21540000']:
                soma_valores_G61 += row.liq_ate_mes
           

        
        sheet.range('G61').value = soma_valores_G61

    
    if rpnp_data is not None:
        for row in rpnp_data.itertuples():
            if row.fonte == '1500701':
                sheet.range('G68').value = row.valor_anu_ant
            if row.fonte == '31500701':
                sheet.range('G69').value = row.valor_anu_ant
            if row.fonte == '51500701':
                sheet.range('G70').value = row.valor_anu_ant
            if row.fonte == '2500701':
                sheet.range('G71').value = row.valor_anu_ant
            if row.fonte == '32500701':
                sheet.range('G72').value = row.valor_anu_ant
            if row.fonte == '52500701':
                sheet.range('G73').value = row.valor_anu_ant

    
    workbook.save()
    workbook.close()
    app.quit()


caminho_qgr = 'QGR 966 (2).csv'
caminho_ded = 'DED 938 (2).csv'
caminho_rpnp = 'RPNP 1619 (2).csv'
caminho_MDE = 'MDE.xlsx'


qgr_data = process_qgr(caminho_qgr) if caminho_qgr else None
ded_data = process_ded(caminho_ded) if caminho_ded else None
rpnp_data = process_rpnp(caminho_rpnp) if caminho_rpnp else None


fill_MDE(caminho_MDE, qgr_data, ded_data, rpnp_data)
