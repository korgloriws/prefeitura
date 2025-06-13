import streamlit as st
import pandas as pd

def formatar_data(data):
    if pd.isnull(data) or not isinstance(data, str):
        return data
    data = data.zfill(8)  
    dia = data[:2]
    mes = data[2:4]
    ano = data[4:]
    return f'{dia}/{mes}/{ano}'

def formatar_valor(valor):
    if pd.isnull(valor):
        return valor
    try:
        return '{:,.2f}'.format(float(str(valor).replace('.', '').replace(',', '.'))).replace(',', 'v').replace('.', ',').replace('v', '.')
    except ValueError:
        return valor

def converter_valor_para_float(valor):
    try:
        return float(valor.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0.0

def comparar_arquivos(relatorio, anl):
    anl_filtrado = anl[anl['registro'] == 10].copy()
    anl_filtrado['data_doc'] = anl_filtrado['data_doc'].astype(str).apply(formatar_data)
    anl_filtrado['valor_anu'] = anl_filtrado['valor_anu'].apply(formatar_valor)
    relatorio['valor_anu'] = relatorio['valor_anu'].apply(formatar_valor)
    colunas_interesse = ["uo", "num_emp", "data_doc", "valor_anu"]
    relatorio_selecionado = relatorio[colunas_interesse]
    anl_selecionado = anl_filtrado[colunas_interesse]
    combinacao_relatorio = relatorio_selecionado.assign(source='relatorio')
    combinacao_anl = anl_selecionado.assign(source='anl')
    combinado = pd.concat([combinacao_relatorio, combinacao_anl], ignore_index=True)
    duplicados = combinado.duplicated(subset=colunas_interesse, keep=False)
    comparacao = combinado[~duplicados]
    relatorio_selecionado['valor_anu_float'] = relatorio_selecionado['valor_anu'].apply(converter_valor_para_float)
    anl_selecionado['valor_anu_float'] = anl_selecionado['valor_anu'].apply(converter_valor_para_float)
    soma_relatorio = relatorio_selecionado['valor_anu_float'].sum()
    soma_anl = anl_selecionado['valor_anu_float'].sum()
    return comparacao, soma_relatorio, soma_anl

def main():
    st.title('ANL')
    relatorio_file = st.file_uploader('Upload Relatório 1157 CSV', type='csv')
    anl_file = st.file_uploader('Upload ANL CSV', type='csv')

    if relatorio_file and anl_file:
        relatorio = pd.read_csv(relatorio_file, encoding='iso-8859-1', delimiter=';', on_bad_lines='skip')
        anl = pd.read_csv(anl_file, encoding='iso-8859-1', delimiter=';', on_bad_lines='skip')
        comparacao, soma_relatorio, soma_anl = comparar_arquivos(relatorio, anl)
        
        st.write("### Diferenças Encontradas")
        st.dataframe(comparacao)
        
        st.write("### Somatório dos Valores")
        st.write(f"Somatório Relatório: {soma_relatorio}")
        st.write(f"Somatório ANL: {soma_anl}")
        
        output_path = 'comparacao_diferencas.xlsx'
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        comparacao.to_excel(writer, index=False, sheet_name='Diferencas')
        somatorio_df = pd.DataFrame({
            'Arquivo': ['Relatorio', 'ANL'],
            'Somatorio Valor Anu': [soma_relatorio, soma_anl]
        })
        somatorio_df.to_excel(writer, index=False, sheet_name='Somatorios')
        writer.close()

        with open(output_path, 'rb') as f:
            st.download_button('Download Excel', f, file_name='comparacao_diferencas.xlsx')

    st.write("Comparação realizada com sucesso. Verifique o arquivo Excel gerado.")

if __name__ == '__main__':
    main()
