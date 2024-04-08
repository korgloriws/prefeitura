import pandas as pd
import streamlit as st

def converter_valor_monetario(valor):
    try:
        valor_limpo = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
        valor_float = float(valor_limpo)
        return round(valor_float, 2)
    except (ValueError, AttributeError):
        return 0.0

def preparar_valor_monetario(valor):
    if pd.isna(valor) or valor.strip() in ['', '-']:
        return 'R$ 0,00'
    else:
        return 'R$ ' + valor.strip().replace('.', ',')  

def adicionar_discrepancia(lista, conta, coluna, valor_matriz, valor_balancete):
    if isinstance(valor_matriz, (float, int)) and isinstance(valor_balancete, (float, int)):
        valor_matriz_formatado = f'R$ {valor_matriz:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        valor_balancete_formatado = f'R$ {valor_balancete:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        valor_matriz_formatado = valor_matriz
        valor_balancete_formatado = valor_balancete
    
    lista.append({
        'Conta': conta,
        'Coluna': coluna,
        'Valor Matriz': valor_matriz_formatado,
        'Valor Balancete': valor_balancete_formatado
    })

def filtrar_plano_de_contas(plano_df):
    plano_df_filtrado = plano_df[plano_df['tipo_conta'] == '5']
    return set(plano_df_filtrado['cod_contabil'])

def escolher_colunas_balancete(conta):
    excecoes_1 = [
       "112910101000000", "112910102000000", "112910104000000", "113919900000000",
        "121119904000000", "121119905000000", "121219903000000", "123810199000000",
        "521120200000000", "521120101000000", "521129900000000",
        "521120300000000", "521120400000000", "522130300000000", "522130900000000"

    ]
    excecoes_2 = [
         "227210105000000", "227210202000000", "227210203000000", "227210204000000",
        "227210304000000", "227210305000000", "227210402000000",
        "227210403000000", "227210404000000", "2272201010000000", "227220203000000", 
        "621310100000000", "621320000000000", "62133000000000", "621340000000000", 
        "621360000000000", "621390000000000"

    ]
    
    # Para contas de exceção, a lógica de seleção de colunas é invertida
    if conta in excecoes_1:
        colunas_balancete = ['credito_anterior', 'debito_mes', 'credito_mes', 'credito_atual']
        colunas_matriz = ['Saldo Inicial', 'Movimentação Crédito', 'Movimentação Débito', 'Saldo Final']
    elif conta in excecoes_2:
        colunas_balancete = ['debito_anterior', 'debito_mes', 'credito_mes', 'debito_atual']
        colunas_matriz = ['Saldo Inicial', 'Movimentação Crédito', 'Movimentação Débito', 'Saldo Final']
        pass
    else:
        # Lógica padrão para contas não excepcionais
        if conta.startswith(('1', '3', '5', '7')):
            colunas_balancete = ['debito_anterior', 'debito_atual']
            colunas_matriz = ['Saldo Inicial',  'Saldo Final']
        elif conta.startswith(('2', '4', '6', '8')):
            colunas_balancete = ['credito_anterior',  'credito_atual']
            colunas_matriz = ['Saldo Inicial', 'Saldo Final']
    return colunas_matriz, colunas_balancete


def comparar_valores(conta, matriz_df, balancete_df, discrepancias, registros_corretos, contas_tipo_5):
    if conta not in contas_tipo_5:
        return  
    erro_encontrado = False
    row_matriz = matriz_df[matriz_df['CONTA'] == conta].iloc[0] if conta in matriz_df['CONTA'].values else None
    row_balancete = balancete_df[balancete_df['cod_contabil'] == conta].iloc[0] if conta in balancete_df['cod_contabil'].values else None

    colunas_matriz, colunas_balancete = escolher_colunas_balancete(conta)

    for col_matriz, col_balancete in zip(colunas_matriz, colunas_balancete):
        valor_matriz = converter_valor_monetario(preparar_valor_monetario(row_matriz[col_matriz])) if row_matriz is not None else 0.0
        valor_balancete = converter_valor_monetario(preparar_valor_monetario(row_balancete[col_balancete])) if row_balancete is not None else 0.0

        if valor_matriz == 0 and valor_balancete == 0:
            continue

        if valor_matriz != valor_balancete:
            adicionar_discrepancia(discrepancias, conta, col_matriz, valor_matriz, valor_balancete)
            erro_encontrado = True

    if not erro_encontrado and row_matriz is not None and row_balancete is not None:
        adicionar_discrepancia(registros_corretos, conta, 'Todos', 'Ok', 'Ok')

# Função principal
def main():
    st.title('Matriz VS Balancete')

    matriz_file = st.file_uploader("Escolha o arquivo da matriz", type=['xlsx'])
    balancete_file = st.file_uploader("Escolha o arquivo do balancete", type=['xlsx'])
    plano_file = st.file_uploader("Escolha o arquivo do plano de contas", type=['xlsx'])

    if st.button('Comparar Arquivos'):
        if matriz_file is not None and balancete_file is not None and plano_file is not None:
            matriz_df = pd.read_excel(matriz_file, dtype=str)
            balancete_df = pd.read_excel(balancete_file, dtype=str)
            plano_df = pd.read_excel(plano_file, dtype=str)

            contas_tipo_5 = filtrar_plano_de_contas(plano_df)
            contas_matriz = set(matriz_df['CONTA'])
            contas_balancete = set(balancete_df['cod_contabil'].astype(str))

            discrepancias = []
            registros_corretos = []

            for conta in contas_tipo_5.intersection(contas_matriz | contas_balancete):
                comparar_valores(conta, matriz_df, balancete_df, discrepancias, registros_corretos, contas_tipo_5)

            discrepancias_df = pd.DataFrame(discrepancias)
            registros_corretos_df = pd.DataFrame(registros_corretos)

            contas_nao_encontradas_df = pd.DataFrame({
                'Conta': list(contas_tipo_5 | contas_matriz | contas_balancete),
                'Presente no Plano de Contas': ['Sim' if conta in contas_tipo_5 else 'Não' for conta in list(contas_tipo_5 | contas_matriz | contas_balancete)],
                'Presente na Matriz': ['Sim' if conta in contas_matriz else 'Não' for conta in list(contas_tipo_5 | contas_matriz | contas_balancete)],
                'Presente no Balancete': ['Sim' if conta in contas_balancete else 'Não' for conta in list(contas_tipo_5 | contas_matriz | contas_balancete)]
            })

            filename = 'relatorio_inconsistencias.xlsx'
            with pd.ExcelWriter(filename) as writer:
                discrepancias_df.to_excel(writer, sheet_name='Discrepancias', index=False)
                registros_corretos_df.to_excel(writer, sheet_name='Corretos', index=False)
                contas_nao_encontradas_df.to_excel(writer, sheet_name='Contas Não Encontradas', index=False)

            st.success(f"Relatório '{filename}' criado com sucesso.")
            
            with open(filename, 'rb') as file:
                st.download_button("Baixar Relatório", file, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        else:
            st.error("Por favor, carregue todos os arquivos necessários.")

if __name__ == "__main__":
    main()
