import streamlit as st
import xlwings as xw
import os
import tempfile

def main():
    st.title('RREO-07-Integrador')

   
    arquivo_xls_origem = st.file_uploader('Relatório sicof', type=['xls', 'xlsx'])
    arquivo_xls_destino = st.file_uploader('planilha vazia do siconfi', type=['xls', 'xlsx'])

    nome_arquivo_copia = st.text_input('Nome do arquivo de cópia:', 'RREO-07.xls')

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
        sheet_destino = wb_destino.sheets['RREO-Anexo 07']

        
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
    "C2": "B23", "D2": "C23", "F2": "D23", "E2": "E23",
    "G2": "F23", "H2": "G23", "I2": "H23", "K2": "I23",
    "L2": "J23", "J2": "K23", "M2": "L23", "C3": "B25",
    "D3": "C25", "F3": "D25", "E3": "E25", "G3": "F25",
    "H3": "G25", "I3": "H25", "K3": "I25", "L3": "J25",
    "J3": "K25", "M3": "L25", "C4": "B27", "D4": "C27",
    "F4": "D27", "E4": "E27", "G4": "F27", "H4": "G27",
    "I4": "H27", "K4": "I27", "L4": "J27", "J4": "K27",
    "M4": "L27", "C4":"B40", "D4":"C40","F4":"D40",
}

if __name__ == "__main__":
    main()


