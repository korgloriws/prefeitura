import streamlit as st
import pandas as pd
import io

def read_and_clean(file):
    df = pd.read_excel(file)
    if "contacontabil" in df.columns and "saldo final" in df.columns:
        df['contacontabil'] = df['contacontabil'].astype(str).str.lower().str.strip()
        df['saldo final'] = df['saldo final'].apply(pd.to_numeric, errors='coerce')
        return df
    else:
        st.error("Colunas 'contacontabil' e/ou 'saldo final' não encontradas.")
        return None

def compare_dfs(df1, df2):
    merged = pd.merge(df1, df2, on='contacontabil', how='outer', suffixes=('_Sicon', '_Sicof'))
    merged['diff_saldo_final'] = merged['saldo final_Sicon'] - merged['saldo final_Sicof']
    filtered = merged[merged['diff_saldo_final'].notna() & (merged['diff_saldo_final'] != 0)]
    filtered = filtered[['contacontabil', 'saldo final_Sicon', 'saldo final_Sicof', 'diff_saldo_final']]
    filtered.columns = ['Conta Contábil', 'Saldo Final (Balancete Sicon)', 'Saldo Final (Balancete Sicof)', 'Diferença de Saldo']
    return merged, filtered

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

def main():
    st.title("Comparador de Balancetes Sicon e Sicof")

    uploaded_file1 = st.file_uploader("Escolha o arquivo Balancete Sicon", type=['xlsx'])
    uploaded_file2 = st.file_uploader("Escolha o arquivo Balancete Sicof", type=['xlsx'])

    if uploaded_file1 and uploaded_file2:
        df1 = read_and_clean(uploaded_file1)
        df2 = read_and_clean(uploaded_file2)
        
        if df1 is not None and df2 is not None:
            full_comparison, differences_only = compare_dfs(df1, df2)
            st.write("Resultado da Comparação Completa:")
            st.write(full_comparison)
            st.write("Resultado da Comparação (Apenas Diferenças):")
            st.write(differences_only)

            if st.button('Gerar Arquivos Excel'):
                full_comp_excel = to_excel(full_comparison)
                diff_only_excel = to_excel(differences_only)
                
                st.download_button(
                    label="Download Comparação Completa",
                    data=full_comp_excel,
                    file_name='Comparação_Completa.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                st.download_button(
                    label="Download Apenas Diferenças",
                    data=diff_only_excel,
                    file_name='Apenas_Diferenças.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

if __name__ == "__main__":
    main()
