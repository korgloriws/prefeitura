import pandas as pd
import xlwings as xw

def soma_valores_correspondentes(df_csv, codigos_excel, co_excel, fonte_recurso_excel):
    filtro_codigos = df_csv['CODIGO_RECEITA'].apply(lambda x: any(str(x).startswith(''.join(filter(str.isdigit, c))) for c in codigos_excel))
    
    
    if pd.isna(co_excel):
        filtro_co = pd.Series([True] * len(df_csv))
    else:
        filtro_co = df_csv['CO'] == co_excel

    if pd.isna(fonte_recurso_excel):
        filtro_fonte_recurso = pd.Series([True] * len(df_csv))
    else:
        filtro_fonte_recurso = df_csv['FONTE_RECURSO'] == fonte_recurso_excel

    filtro_final = filtro_codigos & filtro_co & filtro_fonte_recurso
    
    soma_valores = df_csv.loc[filtro_final, 'VR_ARREC_MES_FONTE'].sum()
    
    return soma_valores


# Carregar o CSV
csv_path = 'QGR MARÇO 2024.csv'
df_csv = pd.read_csv(csv_path, sep=';', encoding='cp1252', usecols=["CODIGO_RECEITA", "FONTE_RECURSO", "CO", "VR_ARREC_MES_FONTE"])
df_csv['VR_ARREC_MES_FONTE'] = df_csv['VR_ARREC_MES_FONTE'].str.replace('.', '').str.replace(',', '.').astype(float)

# Abrir o arquivo Excel
excel_path = 'MODELO RECEITA CORRENTE LÍQUIDA.xlsx'
app = xw.App(visible=True)
book = xw.Book(excel_path)
sheet = book.sheets['Rascunho (2)']

inicio_linha_excel = 8
fim_linha_excel = 41

for i in range(inicio_linha_excel, fim_linha_excel + 1):
    codigo_excel = sheet.range(f'B{i}').value
    co_excel = sheet.range(f'C{i}').value
    fonte_recurso_excel = sheet.range(f'D{i}').value
    
    if not codigo_excel:
        print(f"Nenhum código encontrado na linha {i}, pulando.")
        continue

    codigos_excel = [c.strip() for c in str(codigo_excel).split(',')]
    soma_valores = soma_valores_correspondentes(df_csv, codigos_excel, co_excel, fonte_recurso_excel)

    if soma_valores > 0:
        valor_str = f"{soma_valores:.2f}".replace('.', ',')
        sheet.range(f'E{i}').value = valor_str
        print(f"Atualizado para {valor_str} na linha {i}.")
    else:
        print(f"Nenhuma correspondência encontrada para os códigos {codigo_excel} na linha {i}.")

book.save()
book.close()
app.quit()
