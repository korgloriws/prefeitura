import xlwings as xw
import os


caminho_xls_origem = 'Relatório 6147 - RP Poder e Órgão.xls'  
caminho_xls_original = 'SICONFI_RREO_3118601_20230104_v11 (3).xls'


nome_arquivo_copia = 'copia_preenchida_SICONFI_RREO.xls'
caminho_pasta = os.path.dirname(caminho_xls_original)
caminho_xls_copia = os.path.join(caminho_pasta, nome_arquivo_copia)

app = xw.App(visible=False)
wb_destino = app.books.open(caminho_xls_original)
sheet_destino = wb_destino.sheets['RREO-Anexo 07']


wb_origem = app.books.open(caminho_xls_origem)
sheet_origem = wb_origem.sheets[0] 


def ref_para_indices(ref):
    col_num = 0
    row_part = ''
    for char in ref:
        if char.isdigit():
            row_part += char
        else:
            col_num = col_num * 26 + (ord(char.upper()) - ord('A') + 1)
    row_index = int(row_part) - 1
    col_index = col_num - 1
    return row_index, col_index

mapeamento = {
    "C2": "B23", "D2": "C23", "F2": "D23", "E2": "E23",
    "G2": "F23", "H2": "G23", "I2": "H23", "K2": "I23",
    "L2": "J23", "J2": "K23", "M2": "L23", "C3": "B24",
    "D3": "C24", "F3": "D24", "E3": "E24", "G3": "F24",
    "H3": "G24", "I3": "H24", "K3": "I24", "L3": "J24",
    "J3": "K24", "M3": "L24", "C4": "B27", "D4": "C27",
    "F4": "D27", "E4": "E27", "G4": "F27", "H4": "G27",
    "I4": "H27", "K4": "I27", "L4": "J27", "J4": "K27",
    "M4": "L27",
}



for origem, destino in mapeamento.items():
    valor = sheet_origem.range(origem).value
    sheet_destino.range(destino).value = valor


wb_destino.save(caminho_xls_copia)
wb_destino.close()
wb_origem.close()
app.quit()
