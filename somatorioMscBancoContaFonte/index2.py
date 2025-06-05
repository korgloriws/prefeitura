import pandas as pd


file_path = 'somatorioMscBancoContaFonte/MSC 12_2024 3  APÓS DEPARA.xlsx'
df = pd.read_excel(file_path)


contas_desejadas = [
    '111110100', '111110200', '111110602',
    '111110603','111110604', 
    '111111900', '111115000','114410102','114410105','114410108',
    '114410201','114410303','114410401','114411102',
    '114411105','114413000','111310300',
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


period_changes = calcular_period_change(df_filtrado)


resultados = []

for balance in beginning_balances:
    conta, fonte, tipo, valor = balance
    period_change_c = next((change[4] for change in period_changes if change[0] == conta and change[1] == fonte and change[3] == 'C'), 0)
    period_change_d = next((change[4] for change in period_changes if change[0] == conta and change[1] == fonte and change[3] == 'D'), 0)
    ending_balance = next((end[3] for end in ending_balances if end[0] == conta and end[1] == fonte), 0)
    resultados.append([conta, fonte, valor, period_change_c, period_change_d, ending_balance])

df_resultados = pd.DataFrame(resultados, columns=['CONTA', 'IC3', 'beginning_balance', 'period_change_C', 'period_change_D', 'ending_balance'])


print("Resultados Calculados:")
print(df_resultados)


try:
    with pd.ExcelWriter('resultados3.xlsx', engine='openpyxl') as writer:
        df_resultados.to_excel(writer, index=False)
    print("Arquivo de resultados salvo com sucesso.")
except Exception as e:
    print(f"Erro ao salvar o arquivo: {e}")
