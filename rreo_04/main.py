import streamlit as st
import xlwings as xw
import os
import tempfile

def main():
    st.title('RREO-04-Integrador')

   
    arquivo_xls_origem = st.file_uploader('Relatório sicof', type=['xls', 'xlsx'])
    arquivo_xls_destino = st.file_uploader('planilha vazia do siconfi', type=['xls', 'xlsx'])

    nome_arquivo_copia = st.text_input('Nome do arquivo de cópia:', 'RREO-04.xls')

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
        sheet_destino = wb_destino.sheets['RREO-Anexo 04']

        
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
    "B4":"B22",
"C4":"C22",
"B5":"B23",
"C5":"C23",
"B6":"B24",
"C6":"C24",
"B8":"B26",
"C8":"C26",
"B9":"B27",
"C9":"C27",
"B10":"B28",
"C10":"C28",
"B12":"B30",
"C12":"C30",
"B13":"B31",
"C13":"C31",
"B14":"B32",
"C14":"C32",
"B15":"B33",
"C15":"C33",
"B17":"B35",
"C17":"C35",
"B18":"B36",
"C18":"C36",
"B19":"B37",
"C19":"C37",
"B20":"B39",
"C20":"C39",
"B21":"B40",
"C21":"C40",
"B22":"B41",
"C22":"C41",
"B25":"B52",
"C25":"C52",
"D25":"D52",
"E25":"E52",

"B26":"B53",
"C26":"C53",
"D26":"D53",
"E26":"E53",

"B28":"B55",
"C28":"C55",
"D28":"D55",
"E28":"E55",

"B29":"B56",
"C29":"C56",
"D29":"D56",
"E29":"E56",

"B31":"B85",
"B32":"B86",
"B33":"B87",
"B34":"B88",
"B36":"B97",
"B37":"B98",
"B38":"B99",
"B41":"B110",
"C41":"C110",
"B42":"B111",
"C42":"C111",
"B43":"B112",
"C43":"C112",
"B45":"B114",
"C45":"C114",
"B46":"B115",
"C46":"C115",
"B47":"B116",
"C47":"C116",
"B49":"B118",
"C49":"C118",
"B50":"B119",
"C50":"C119",
"B51":"B120",
"C51":"C120",
"B52":"B121",
"C52":"C121",
"B54":"B123",
"C54":"C123",
"B55":"B124",
"C55":"C124",
"B56":"B126",
"C56":"C126",
"B59":"B139",
"C59":"C139",
"D59":"D139",
"E59":"E139",

"B60":"B140",
"C60":"C140",
"D60":"D140",
"E60":"E140",
"F60":"F140",
"B62":"B142",
"C62":"C142",
"D62":"D142",
"E62":"E142",

"B63":"B143",
"C63":"C143",
"D63":"D143",
"E63":"E143",

"B65":"B154",
"B66":"B155",
"B68":"B164",
"B69":"B165",
"B70":"B166",
"B72":"B175",
"C72":"C175",
"B74":"B187",
"C74":"C187",
"D74":"D187",
"E74":"E187",

"B75":"B186",
"C75":"C186",
"D75":"D186",
"E75":"E186",

"B76":"B188",
"C76":"C188",
"D76":"D188",
"E76":"E188",

"B78":"B199",
"B79":"B200",
"B80":"B201",

}

if __name__ == "__main__":
    main()


