import streamlit as st
import xlwings as xw
import tempfile
import os

def valor_numerico_ajustado(valor):
   
    try:
        valor_ajustado = round(float(valor), 2)
        return 0 if valor_ajustado == 0 else valor_ajustado
    except (ValueError, TypeError):
        return valor  
def valor_equivalente_a_zero(valor):
    
    if valor is None or valor == '' or (isinstance(valor, (int, float)) and valor == 0):
        return True
    try:
        
        return float(valor) == 0.0
    except ValueError:
        
        return False

def comparar_intervalo(sheet1, sheet2, inicio='A1', fim='L413'):
    discrepancias = []
    for celula in sheet1.range(f'{inicio}:{fim}'):
      
        coluna_celula = celula.get_address(0, 0)[0]
        
        
        if coluna_celula == 'J' or coluna_celula == 'F':
            continue
        
        valor1 = celula.value
        valor2 = sheet2.range(celula.address).value
        
       
        if isinstance(valor1, (int, float)) and isinstance(valor2, (int, float)):
            valor1 = round(valor1, 2)
            valor2 = round(valor2, 2)

       
        if valor_equivalente_a_zero(valor1) and valor_equivalente_a_zero(valor2):
            continue  

        if valor1 != valor2:
            discrepancias.append((celula.address, valor1, valor2))
    return discrepancias



def gerar_relatorio_discrepancias(discrepancias, caminho_salvar):
   
    with xw.App(visible=False) as app:
        wb = app.books.add()
        sheet = wb.sheets[0]
        sheet.range('A1').value = ['Célula', 'siconf', 'integrador']
        for i, discrep in enumerate(discrepancias, start=2):
            sheet.range(f'A{i}:C{i}').value = discrep
        wb.save(caminho_salvar)
        wb.close()

def main():
    st.title('Comparador RREO Anexo 02')

    arquivo_xls_1 = st.file_uploader('RREO gerada pelo siconfi', type=['xls', 'xlsx'], key="file1")
    arquivo_xls_2 = st.file_uploader('planilha gerada pelo integrador', type=['xls', 'xlsx'], key="file2")

    if st.button('Comparar Arquivos'):
        if arquivo_xls_1 and arquivo_xls_2:
            caminho_xls_1, caminho_xls_2 = None, None
            try:
               
                caminho_xls_1 = salvar_arquivo_temporario(arquivo_xls_1, suffix='.xlsx')
                caminho_xls_2 = salvar_arquivo_temporario(arquivo_xls_2, suffix='.xlsx')

                app = xw.App(visible=False)
                wb1 = app.books.open(caminho_xls_1)
                wb2 = app.books.open(caminho_xls_2)
                sheet1 = wb1.sheets['RREO-Anexo 02']
                sheet2 = wb2.sheets['RREO-Anexo 02']

                discrepancias = comparar_intervalo(sheet1, sheet2)

               
                
                if discrepancias:
                    st.error('Foram encontradas discrepâncias:')
                    for celula, valor1, valor2 in discrepancias:
                        st.write(f'{celula}: Valor 1 = {valor1}, Valor 2 = {valor2}')
                    
                   
                    caminho_relatorio = tempfile.mktemp(suffix='.xlsx')
                    gerar_relatorio_discrepancias(discrepancias, caminho_relatorio)
                    with open(caminho_relatorio, "rb") as file:
                        st.download_button(label="Download relatório de discrepâncias", data=file, file_name="relatorio_discrepancias.xlsx")
                else:
                    st.success('Nenhuma discrepância encontrada entre os arquivos.')
            except Exception as e:
                st.error(f'Ocorreu um erro: {e}')
            finally:
                if 'wb1' in locals():
                    wb1.close()
                if 'wb2' in locals():
                    wb2.close()
                if 'app' in locals():
                    app.quit()
                if caminho_xls_1:
                    os.remove(caminho_xls_1)
                if caminho_xls_2:
                    os.remove(caminho_xls_2)

def salvar_arquivo_temporario(uploaded_file, suffix):
   
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_file_path, "wb") as tmp_file:
       
        tmp_file.write(uploaded_file.getvalue())
    return temp_file_path


if __name__ == "__main__":
    main()
