import streamlit as st
import pandas as pd
import io

def calcular_valores(sub_df):
    conta = sub_df['CONTA'].iloc[0]
    
    excecoes_dc = [
        "112910101000000", "112910102000000", "112910104000000", "113919900000000", "121119904000000", "121119905000000", "121219903000000", "123810199000000", 
        "521120101000000", "52112020000000", "521120300000000", "521120400000000", "521129900000000", "522130300000000", "522130900000000"  
    ]
    excecoes_cd = [
        "227210103000000", "227210105000000", "227210202000000", "227210203000000", "227210204000000", "227210303000000", "227210304000000", "227210305000000", 
        "227210402000000", "227210403000000", "227210404000000", "227220101000000", "227220203000000", "621310100000000", "621320000000000", "621330000000000", 
        "621340000000000", "621360000000000", "621390000000000"
    ]
    
    if conta[0] in ['1', '3', '5', '7']:
        if conta in excecoes_dc:
            operacao = lambda d, c: c - d
        else:
            operacao = lambda d, c: d - c
    else:
        if conta in excecoes_cd:
            operacao = lambda d, c: d - c
        else:
            operacao = lambda d, c: c - d
    
    saldo_inicial = operacao(
        sub_df[(sub_df['Tipo_valor'] == 'beginning_balance') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum(),
        sub_df[(sub_df['Tipo_valor'] == 'beginning_balance') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    )
    
    saldo_final = operacao(
        sub_df[(sub_df['Tipo_valor'] == 'ending_balance') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum(),
        sub_df[(sub_df['Tipo_valor'] == 'ending_balance') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    )
    
    mov_credito = sub_df[(sub_df['Tipo_valor'] == 'period_change') & (sub_df['Natureza_valor'] == 'C')]['Valor'].sum()
    mov_debito = sub_df[(sub_df['Tipo_valor'] == 'period_change') & (sub_df['Natureza_valor'] == 'D')]['Valor'].sum()

    saldo_inicial, saldo_final, mov_credito, mov_debito = map(lambda x: round(x, 2), [saldo_inicial, saldo_final, mov_credito, mov_debito])

    if conta[0] in ['1', '3', '5', '7']:
        natureza_final = 'D' if saldo_final >= 0 else 'C'
    else:
        natureza_final = 'C' if saldo_final >= 0 else 'D'
    
    return pd.Series([saldo_inicial, mov_debito, mov_credito, saldo_final, natureza_final])

def adicionar_observacoes(row):
    conta_inicial = str(row['CONTA'])[0]  
    saldo_final = row['Saldo Final']
    natureza_final = row['Natureza Final']
    
    if saldo_final != 0:
        if conta_inicial == '1' and natureza_final != 'D':
            return 'saldo invertido'
        elif conta_inicial == '2' and natureza_final != 'C':
            return 'saldo invertido'
        elif conta_inicial == '3' and natureza_final not in ['D']:
            return 'posição inválida'
        elif conta_inicial == '4' and natureza_final not in ['C']:
            return 'posição inválida'
        elif conta_inicial == '5' and natureza_final != 'D':
            return 'saldo invertido'
        elif conta_inicial == '6' and natureza_final != 'C':
            return 'saldo invertido'
        elif conta_inicial == '7' and natureza_final != 'D':
            return 'saldo invertido'
        elif conta_inicial == '8' and natureza_final != 'C':
            return 'saldo invertido'
    return ''

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file, sep=';', dtype={'CONTA': str})
    df['Valor'] = df['Valor'].str.replace(',', '.').astype(float)
    resultado = df.groupby('CONTA').apply(calcular_valores)
    resultado.columns = ['Saldo Inicial', 'Movimentação Débito', 'Movimentação Crédito', 'Saldo Final', 'Natureza Final']
    resultado = resultado.reset_index()  
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

    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
    if uploaded_file is not None:
        resultado = process_file(uploaded_file)

        st.write("Resultados:")
        st.dataframe(resultado)

        result_excel = generate_excel(resultado)
        st.download_button(label="Baixar Excel",
                           data=result_excel,
                           file_name='matrizCorrigida.xlsx',
                           mime='application/vnd.ms-excel')

if __name__ == "__main__":
    main()
