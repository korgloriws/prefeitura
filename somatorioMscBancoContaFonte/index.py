import pandas as pd


file_path = 'MSC 12_2024 3  APÓS DEPARA.xlsx'
df = pd.read_excel(file_path)

contas_desejadas = [
    '111110100', '111110200', '111110602',
    '111110603', '111111900', '111115000'
]


df = df[['CONTA', 'IC3', 'Valor', 'Tipo_valor', 'Natureza_valor']]


df_filtrado = df[df['CONTA'].astype(str).isin(contas_desejadas)]


print("DataFrame Filtrado:")
print(df_filtrado.head())


def calcular_balance(df, tipo_valor):
    balances = []
    for conta in contas_desejadas:
        df_conta = df[df['CONTA'].astype(str) == conta]
        fontes = df_conta['IC3'].unique()
        for fonte in fontes:
            df_fonte = df_conta[df_conta['IC3'] == fonte]
            c_sum = df_fonte[(df_fonte['Tipo_valor'] == tipo_valor) & (df_fonte['Natureza_valor'] == 'C')]['Valor'].sum()
            d_sum = df_fonte[(df_fonte['Tipo_valor'] == tipo_valor) & (df_fonte['Natureza_valor'] == 'D')]['Valor'].sum()
            balance = d_sum - c_sum
            balances.append([conta, fonte, tipo_valor, balance])
            print(f"Conta: {conta}, Fonte: {fonte}, Tipo: {tipo_valor}, D: {d_sum}, C: {c_sum}, Balance: {balance}")  
    return balances


def calcular_period_change(df):
    changes = []
    for conta in contas_desejadas:
        df_conta = df[df['CONTA'].astype(str) == conta]
        fontes = df_conta['IC3'].unique()
        for fonte in fontes:
            df_fonte = df_conta[df_conta['IC3'] == fonte]
            c_sum = df_fonte[(df_fonte['Tipo_valor'] == 'period_change') & (df_fonte['Natureza_valor'] == 'C')]['Valor'].sum()
            d_sum = df_fonte[(df_fonte['Tipo_valor'] == 'period_change') & (df_fonte['Natureza_valor'] == 'D')]['Valor'].sum()
            changes.append([conta, fonte, 'period_change', 'C', c_sum])
            changes.append([conta, fonte, 'period_change', 'D', d_sum])
            print(f"Conta: {conta}, Fonte: {fonte}, Period Change C: {c_sum}, Period Change D: {d_sum}")  
    return changes

beginning_balances = calcular_balance(df_filtrado, 'beginning_balance')
ending_balances = calcular_balance(df_filtrado, 'ending_balance')

print("Beginning Balances:")
print(beginning_balances)
print("Ending Balances:")
print(ending_balances)


period_changes = calcular_period_change(df_filtrado)

print("Period Changes:")
print(period_changes)


resultados = pd.DataFrame(columns=['CONTA', 'IC3', 'Tipo_valor', 'Natureza_valor', 'Valor'])


for balance in beginning_balances:
    print(f"Adding beginning balance: {balance}")  
    resultados = pd.concat([resultados, pd.DataFrame([[balance[0], balance[1], balance[2], '', balance[3]]], columns=['CONTA', 'IC3', 'Tipo_valor', 'Natureza_valor', 'Valor'])], ignore_index=True)

for balance in ending_balances:
    print(f"Adding ending balance: {balance}") 
    resultados = pd.concat([resultados, pd.DataFrame([[balance[0], balance[1], balance[2], '', balance[3]]], columns=['CONTA', 'IC3', 'Tipo_valor', 'Natureza_valor', 'Valor'])], ignore_index=True)


for change in period_changes:
    print(f"Adding period change: {change}")
    resultados = pd.concat([resultados, pd.DataFrame([[change[0], change[1], change[2], change[3], change[4]]], columns=['CONTA', 'IC3', 'Tipo_valor', 'Natureza_valor', 'Valor'])], ignore_index=True)


print("Resultados Calculados:")
print(resultados)


try:
    with pd.ExcelWriter('resultados1.xlsx', engine='openpyxl') as writer:
        resultados.to_excel(writer, index=False)
    print("Arquivo de resultados salvo com sucesso.")
except Exception as e:
    print(f"Erro ao salvar o arquivo: {e}")
