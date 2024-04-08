import streamlit as st
import xlwings as xw
import os
import tempfile

def main():
    st.title('RREO-01-Integrador')

  
    arquivo_xls_origem = st.file_uploader('Relatório sicof', type=['xls', 'xlsx'])
    arquivo_xls_destino = st.file_uploader('planilha vazia do siconfi', type=['xls', 'xlsx'])

    nome_arquivo_copia = st.text_input('Nome do arquivo de cópia:', 'RREO-01.xls')

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
        sheet_destino = wb_destino.sheets['RREO-Anexo 01']

        
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
  "C4":"B24",
"D4":"C24",
"E4":"D24",
"F4":"F24",
"G4":"H24",
"C5":"B25",
"D5":"C25",
"E5":"D25",
"F5":"F25",
"G5":"H25",
"C7":"B28",
"D7":"C28",
"E7":"D28",
"F7":"F28",
"G7":"H28",
"C8":"B31",
"D8":"C31",
"E8":"D31",
"F8":"F31",
"G8":"H31",
"C10":"B33",
"D10":"C33",
"E10":"D33",
"F10":"F33",
"G10":"H33",
"C11":"B34",
"D11":"C34",
"E11":"D34",
"F11":"F34",
"G11":"H34",
"C13":"B43",
"D13":"C43",
"E13":"D43",
"F13":"F43",
"G13":"H43",
"C14":"B44",
"D14":"C44",
"E14":"D44",
"F14":"F44",
"G14":"H44",
"C15":"B47",
"D15":"C47",
"E15":"D47",
"F15":"F47",
"G15":"H47",
"C17":"B49",
"D17":"C49",
"E17":"D49",
"F17":"F49",
"G17":"H49",
"C18":"B50",
"D18":"C50",
"E18":"D50",
"F18":"F50",
"G18":"H50",
"C19":"B52",
"D19":"C52",
"E19":"D52",
"F19":"F52",
"G19":"H52",
"C20":"B53",
"D20":"C53",
"E20":"D53",
"F20":"F53",
"G20":"H53",
"C22":"B57",
"D22":"C57",
"E22":"D57",
"F22":"F57",
"G22":"H57",
"C23":"B58",
"D23":"C58",
"E23":"D58",
"F23":"F58",
"G23":"H58",
"C24":"B61",
"D24":"C61",
"E24":"D61",
"F24":"F61",
"G24":"H61",
"C27":"B64",
"D27":"C64",
"E27":"D64",
"F27":"F64",
"G27":"H64",
"C28":"B65",
"D28":"C65",
"E28":"D65",
"F28":"F65",
"G28":"H65",
"C30":"B67",
"D30":"C67",
"E30":"D67",
"F30":"F67",
"G30":"H67",
"C32":"B72",
"D32":"C72",
"E32":"D72",
"F32":"F72",
"G32":"H72",
"C33":"B73",
"D33":"C73",
"E33":"D73",
"F33":"F73",
"G33":"H73",
"C34":"B75",
"D34":"C75",
"E34":"D75",
"F34":"F75",
"G34":"H75",
"C36":"B83",
"D36":"C83",
"E36":"D83",
"F36":"F83",
"G36":"H83",
"C40":"B146",
"D40":"C146",
"E40":"D146",
"F40":"F146",
"G40":"H146",
"C42":"B179",
"D42":"C179",
"E42":"D179",
"F42":"F179",
"G42":"H179",
"C45":"B109",
"D45":"C109",
"E45":"D109",
"F45":"E109",
"G45":"G109",
"H45":"H109",
"J45":"J109",
"K45":"I109",
"C46":"B110",
"D46":"C110",
"E46":"D110",
"F46":"E110",
"G46":"G110",
"H46":"H110",
"J46":"J110",
"K46":"I110",
"C47":"B111",
"D47":"C111",
"E47":"D111",
"F47":"E111",
"G47":"G111",
"H47":"H111",
"J47":"J111",
"K47":"I111",
"C49":"B113",
"D49":"C113",
"E49":"D113",
"F49":"E113",
"G49":"G113",
"H49":"H113",
"J49":"J113",
"K49":"I113",
"C50":"B115",
"D50":"C115",
"E50":"D115",
"F50":"E115",
"G50":"G115",
"H50":"H115",
"J50":"J115",
"K50":"I115",
"C51":"B116",
"D51":"C116",
"E51":"D116",
"F51":"E116",
"G51":"G116",
"H51":"H116",
"J51":"J116",
"K51":"I116",
"C54":"B212",
"D54":"C212",
"E54":"D212",
"F54":"E212",
"G54":"G212",
"H54":"H212",
"J54":"J212",
"K54":"I212",
"C55":"B214",
"D55":"C214",
"E55":"D214",
"F55":"E214",
"G55":"G214",
"H55":"H214",
"J55":"J214",
"K55":"I214",
}

if __name__ == "__main__":
    main()
