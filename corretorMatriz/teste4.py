import streamlit as st
import pandas as pd
import io
from decimal import Decimal

excecoes_dc = [
    "112910101000000", "112910102000000", "112910104000000", "113919900000000", "123810105000000",
    "123810101000000","121119904000000", "121119905000000", "121219903000000", "123810199000000",
    "123810102000000","123810205000000","521120200000000", "521120101000000", "521129900000000",
    "113910402000000","121119999000000","123810104000000","521120300000000", "521120400000000",
    "522130300000000", "522130900000000","123810103000000","522139900000000"
]

excecoes_cd = [
    "227210105000000", "227210202000000", "227210203000000", "227210204000000",
    "227210304000000", "227210305000000", "227210402000000","227210104000000",
    "227210403000000", "227210404000000", "2272201010000000", "227220203000000", 
    "621310100000000", "621320000000000", "62133000000000", "621340000000000",
    "621360000000000", "621390000000000","621330000000000", "227210303000000","227210103000000",
]

def calcular_valores(sub_df):
    conta = sub_df['CONTA'].iloc[0]
    d_inicial = sub_df[(sub_df['Tipo_valor'] == 'beginning_balance') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum()
    c_inicial = sub_df[(sub_df['Tipo_valor'] == 'beginning_balance') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    d_final = sub_df[(sub_df['Tipo_valor'] == 'ending_balance') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum()
    c_final = sub_df[(sub_df['Tipo_valor'] == 'ending_balance') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    mov_credito = sub_df[(sub_df['Tipo_valor'] == 'period_change') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    mov_debito  = sub_df[(sub_df['Tipo_valor'] == 'period_change') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum()
    
    if conta[0] in ['1','3','5','7']:
        if conta in excecoes_dc:
            raw_saldo_inicial = c_inicial - d_inicial
            raw_saldo_final   = c_final - d_final
            if raw_saldo_final >= 0:
                natureza_final = 'C'
            else:
                natureza_final = 'D'
        else:
            raw_saldo_inicial = d_inicial - c_inicial
            raw_saldo_final   = d_final - c_final
            if raw_saldo_final >= 0:
                natureza_final = 'D'
            else:
                natureza_final = 'C'
    else:
        if conta in excecoes_cd:
            raw_saldo_inicial = d_inicial - c_inicial
            raw_saldo_final   = d_final - c_final
            if raw_saldo_final >= 0:
                natureza_final = 'D'
            else:
                natureza_final = 'C'
        else:
            raw_saldo_inicial = c_inicial - d_inicial
            raw_saldo_final   = c_final - d_final
            if raw_saldo_final >= 0:
                natureza_final = 'C'
            else:
                natureza_final = 'D'

    saldo_inicial = abs(raw_saldo_inicial)
    saldo_final   = abs(raw_saldo_final)
    return pd.Series([saldo_inicial, mov_debito, mov_credito, saldo_final, natureza_final])

def adicionar_observacoes(row):
    conta = row['CONTA']
    conta_inicial = conta[0]
    saldo_final = row['Saldo Final']
    natureza_final = row['Natureza Final']
    if saldo_final != 0:  
        if conta_inicial in ['1','3','5','7']:
            natureza_esperada = 'D'
        else:
            natureza_esperada = 'C'
        if natureza_final != natureza_esperada:
            if (conta not in excecoes_dc) and (conta not in excecoes_cd):
                if conta_inicial in ['1','2','5','6','7','8']:
                    return 'saldo invertido'
                elif conta_inicial in ['3','4']:
                    return 'posição inválida'
    return ''

def process_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, sep=';', dtype={'CONTA': str})
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, dtype={'CONTA': str})
    else:
        st.error("Formato de arquivo não suportado")
        return None

    df['Valor'] = df['Valor'].apply(lambda x: Decimal(str(x)))
    resultado = df.groupby('CONTA').apply(calcular_valores).reset_index()
    resultado.columns = [
        'CONTA',
        'Saldo Inicial',
        'Movimentação Débito',
        'Movimentação Crédito',
        'Saldo Final',
        'Natureza Final'
    ]
    resultado['OBS'] = resultado.apply(adicionar_observacoes, axis=1)
    return resultado

def generate_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

def main():
    st.title("Corretor Matriz")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"])
    if uploaded_file is not None:
        resultado = process_file(uploaded_file)
        if resultado is not None:
            st.write("Resultados:")
            st.dataframe(resultado)
            result_excel = generate_excel(resultado)
            st.download_button(
                label="Baixar Excel",
                data=result_excel,
                file_name='matrizCorrigida.xlsx',
                mime='application/vnd.ms-excel'
            )

if __name__ == "__main__":
    main()
