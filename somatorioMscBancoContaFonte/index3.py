import streamlit as st
import pandas as pd
from io import BytesIO

def main():
    st.title("Somatório MSC Banco Conta Fonte")

    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        contas_desejadas = [
            '111110100', '111110200', '111110602',
            '111110603','111110604', 
            '111111900', '111115000','114410102','114410105','114410108',
            '114410201','114410303','114410401','114411102',
            '114411105','114413000','111310300',
        ]

        df = df[['CONTA', 'IC3', 'Valor', 'Tipo_valor', 'Natureza_valor']]

        df_filtrado = df[df['CONTA'].astype(str).isin(contas_desejadas)]

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

    
        st.write(df_resultados)


        df_soma_ic3 = df_resultados.groupby('IC3')['ending_balance'].sum().reset_index()
        df_soma_ic3.columns = ['IC3', 'Soma_ending_balance']

       
        st.write(df_soma_ic3)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
            df_soma_ic3.to_excel(writer, sheet_name='Soma_IC3', index=False)
        output.seek(0)

        st.download_button(
            label="Baixar Resultados",
            data=output,
            file_name='resultados3.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main()
