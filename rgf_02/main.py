import streamlit as st
import xlwings as xw
import os
import tempfile

def main():
    st.title('RGF-02-Integrador')

   
    arquivo_xls_origem = st.file_uploader('Relatório sicof', type=['xls', 'xlsx'])
    arquivo_xls_destino = st.file_uploader('planilha vazia do siconfi', type=['xls', 'xlsx'])

    nome_arquivo_copia = st.text_input('Nome do arquivo de cópia:', 'RGF-02.xls')

    if st.button('Transferir Dados') and arquivo_xls_origem and arquivo_xls_destino:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xls') as tmp_origem:
            tmp_origem.write(arquivo_xls_origem.getvalue())
            caminho_xls_origem = tmp_origem.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xls') as tmp_destino:
            tmp_destino.write(arquivo_xls_destino.getvalue())
            caminho_xls_original = tmp_destino.name

        caminho_pasta = tempfile.gettempdir()
        caminho_xls_copia = os.path.join(caminho_pasta, nome_arquivo_copia)

       
        app = xw.App(visible=False)
        wb_destino = app.books.open(caminho_xls_original)
        sheet_destino = wb_destino.sheets['RGF-Anexo 02']

        
        wb_origem = app.books.open(caminho_xls_origem)
        sheet_origem = wb_origem.sheets[0]  

       
        for origem, destino in mapeamento.items():
            valor = sheet_origem.range(origem).value
            sheet_destino.range(destino).value = valor

        
        wb_destino.save(caminho_xls_copia)
        wb_destino.close()
        wb_origem.close()
        app.quit()

      
        with open(caminho_xls_copia, "rb") as file:
            btn = st.download_button(
                label="Download arquivo copiado",
                data=file,
                file_name=nome_arquivo_copia,
                mime="application/vnd.ms-excel"
            )
        st.success('Dados transferidos com sucesso.')

mapeamento = {
    "B3":"B22",
"C3":"C22",
"D3":"D22",
"E3":"E22",
"B6":"B25",
"C6":"C25",
"D6":"D25",
"E6":"E25",
"B7":"B26",
"C7":"C26",
"D7":"D26",
"E7":"E26",
"B8":"B27",
"C8":"C27",
"D8":"D27",
"E8":"E27",
"B10":"B29",
"C10":"C29",
"D10":"D29",
"E10":"E29",
"B11":"B30",
"C11":"C30",
"D11":"D30",
"E11":"E30",
"B13":"B32",
"C13":"C32",
"D13":"D32",
"E13":"E32",
"B14":"B33",
"C14":"C33",
"D14":"D33",
"E14":"E33",
"B15":"B34",
"C15":"C34",
"D15":"D34",
"E15":"E34",
"B16":"B35",
"C16":"C35",
"D16":"D35",
"E16":"E35",
"B17":"B36",
"C17":"C36",
"D17":"D36",
"E17":"E36",
"B18":"B37",
"C18":"C37",
"D18":"D37",
"E18":"E37",
"B19":"B38",
"C19":"C38",
"D19":"D38",
"E19":"E38",
"B20":"B39",
"C20":"C39",
"D20":"D39",
"E20":"E39",
"B23":"B42",
"C23":"C42",
"D23":"D42",
"E23":"E42",
"B24":"B43",
"C24":"C43",
"D24":"D43",
"E24":"E43",
"B25":"B44",
"C25":"C44",
"D25":"D44",
"E25":"E44",
"B26":"B45",
"C26":"C45",
"D26":"D45",
"E26":"E45",

}

if __name__ == "__main__":
    main()
