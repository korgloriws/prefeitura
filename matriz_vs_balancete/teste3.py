import pandas as pd
import streamlit as st

def converter_valor_monetario(valor):
    try:
        valor_limpo = (
            valor.replace('R$', '')
                 .replace('.', '')
                 .replace(',', '.')
                 .strip()
        )
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

def escolher_colunas_balancete(conta, natureza_final=None):

    excecoes_1 = {
       "112910101000000", "112910102000000", "112910104000000", "113919900000000","123810105000000","123810101000000",
       "121119904000000", "121119905000000", "121219903000000", "123810199000000","123810102000000","123810205000000",
       "521120200000000", "521120101000000", "521129900000000", "113910402000000","121119999000000","123810104000000",
       "521120300000000", "521120400000000", "522130300000000", "522130900000000","123810103000000",
    }
    excecoes_2 = {
         "227210105000000", "227210202000000", "227210203000000", "227210204000000",
         "227210304000000", "227210305000000", "227210402000000","227210104000000",
         "227210403000000", "227210404000000", "2272201010000000", "227220203000000", 
         "621310100000000", "621320000000000", "62133000000000", "621340000000000", 
         "621360000000000", "621390000000000","621330000000000", "227210303000000","227210103000000",
    }

    todas_excecoes = excecoes_1.union(excecoes_2)

    CONTAS_HIBRIDAS = {
        "227210500000000","234100000000000","234110000000000","234120000000000","234130000000000","234140000000000",
        "234150000000000","234200000000000","234210000000000","234220000000000","234230000000000","234240000000000",
        "234250000000000","237000000000000","237100000000000","237110000000000","237110100000000","237110200000000",
        "237110300000000","237110301000000","237110302000000","237110400000000","237120000000000","237120100000000",
        "237120200000000","237120300000000","237120400000000","237130000000000","237130100000000","237130200000000",
        "237130300000000","237130400000000","237140000000000","237140100000000","237140200000000","237140300000000",
        "237140400000000","237150000000000","237150100000000","237150200000000","237150300000000","237150400000000",
        "237200000000000","237210000000000","237210100000000","237210101000000","237210200000000","237210201000000",
        "237210202000000","237210300000000","237210400000000","237210500000000","237210600000000","237220000000000",
        "237220100000000","237220200000000","237220300000000","237220400000000","237220500000000","237220600000000",
        "237230000000000","237230100000000","237230200000000","237230300000000","237230400000000","237230500000000",
        "237230600000000","237240000000000","237240100000000","237240200000000","237240300000000","237240400000000",
        "237240500000000","237240600000000","237250000000000","237250100000000","237250200000000","237250300000000",
        "237250400000000","237250500000000","237250600000000","511200000000000","522139900000000","621100000000000",
        "622800000000000","821110000000000","821110100000000","821110200000000","821119900000000"
    }


    colunas_matriz = ['Saldo Inicial','Movimentação Débito','Movimentação Crédito','Saldo Final']

 
    if conta in CONTAS_HIBRIDAS and natureza_final is not None:
        if natureza_final == 'D':
            colunas_balancete = ['debito_anterior','debito_mes','credito_mes','debito_atual']
        elif natureza_final == 'C':
            colunas_balancete = ['credito_anterior','debito_mes','credito_mes','credito_atual']
        else:
            return [], []
        return colunas_matriz, colunas_balancete

 
    if conta.startswith(('1','3','5','7')):

        cols_normal = ['debito_anterior','debito_mes','credito_mes','debito_atual']

        cols_excecao = ['credito_anterior','debito_mes','credito_mes','credito_atual']

        if conta in todas_excecoes:
            return colunas_matriz, cols_excecao
        else:
            return colunas_matriz, cols_normal

    elif conta.startswith(('2','4','6','8')):

        cols_normal = ['credito_anterior','debito_mes','credito_mes','credito_atual']

        cols_excecao = ['debito_anterior','debito_mes','credito_mes','debito_atual']

        if conta in todas_excecoes:
            return colunas_matriz, cols_excecao
        else:
            return colunas_matriz, cols_normal


    return [], []

def comparar_valores(conta, matriz_df, balancete_df, discrepancias, registros_corretos, contas_tipo_5):
    if conta not in contas_tipo_5:
        return  

    erro_encontrado = False


    row_matriz = (
        matriz_df[matriz_df['CONTA'] == conta].iloc[0] 
        if conta in matriz_df['CONTA'].values 
        else None
    )
    row_balancete = (
        balancete_df[balancete_df['cod_contabil'] == conta].iloc[0] 
        if conta in balancete_df['cod_contabil'].values 
        else None
    )

    natureza_final = None
    if row_matriz is not None and 'Natureza Final' in row_matriz and pd.notna(row_matriz['Natureza Final']):
        natureza_final = row_matriz['Natureza Final'].strip()


    colunas_matriz, colunas_balancete = escolher_colunas_balancete(conta, natureza_final)


    for col_matriz, col_balancete in zip(colunas_matriz, colunas_balancete):
        valor_matriz = 0.0
        valor_balancete = 0.0

        if row_matriz is not None and col_matriz in row_matriz:
            valor_matriz = converter_valor_monetario(
                preparar_valor_monetario(row_matriz[col_matriz])
            )
        if row_balancete is not None and col_balancete in row_balancete:
            valor_balancete = converter_valor_monetario(
                preparar_valor_monetario(row_balancete[col_balancete])
            )


        if abs(valor_matriz) == 0 and abs(valor_balancete) == 0:
            continue


        if abs(valor_matriz) != abs(valor_balancete):
            adicionar_discrepancia(discrepancias, conta, col_matriz, valor_matriz, valor_balancete)
            erro_encontrado = True


    if not erro_encontrado and row_matriz is not None and row_balancete is not None:
        adicionar_discrepancia(registros_corretos, conta, 'Todos', 'Ok', 'Ok')

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
