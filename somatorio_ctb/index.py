import pandas as pd

def converter_para_float(valor):
    try:
      
        return float(valor.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0  

try:
    df = pd.read_csv('CTB OUT-23 VALIDADO.csv', sep=';', on_bad_lines='skip')

    
    df['saldo_final'] = df['saldo_final'].apply(converter_para_float)

    df_filtrado = df[df['registro'] == 20]
    resultado = df_filtrado.groupby('fonte')['saldo_final'].sum()

   
    resultado.to_excel('resultado.xlsx', sheet_name='Soma por Fonte')
    print("Relatório gerado com sucesso: resultado.xlsx")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
