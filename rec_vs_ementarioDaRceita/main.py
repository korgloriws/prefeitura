import pandas as pd
import streamlit as st
import os
import tempfile


def ajustar_natureza_receita(natureza):
    natureza = str(natureza)  
    if len(natureza) == 10:
        return natureza[2:] 
    return natureza


def ajustar_fonte_recursos(fonte):
    fonte = str(fonte)  
    if len(fonte) == 7:
        return fonte[1:4]  
    return fonte

def processar_arquivos(ementario_file, rec_file):

    ementario_df = pd.read_excel(ementario_file, sheet_name="COMPATIB REC_FR")
    ementario_df = ementario_df[['NATUREZA DA RECEITA', 'ESPECIFICAÇÃO DA FONTE DE RECURSOS']]


    rec_df = pd.read_excel(rec_file)
    rec_df = rec_df[['NATUREZA DA RECEITA', 'ESPECIFICAÇÃO DA FONTE DE RECURSOS', 'registro']]

    rec_df = rec_df[rec_df['registro'] == 11]


    rec_df['NATUREZA DA RECEITA'] = rec_df['NATUREZA DA RECEITA'].apply(ajustar_natureza_receita)
    rec_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'] = rec_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'].apply(ajustar_fonte_recursos)

    ementario_df['NATUREZA DA RECEITA'] = ementario_df['NATUREZA DA RECEITA'].apply(ajustar_natureza_receita)
    ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'] = ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'].apply(ajustar_fonte_recursos)

    rec_df['NATUREZA DA RECEITA'] = rec_df['NATUREZA DA RECEITA'].astype(str)
    rec_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'] = rec_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'].astype(str)

    ementario_df['NATUREZA DA RECEITA'] = ementario_df['NATUREZA DA RECEITA'].astype(str)
    ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'] = ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'].astype(str)

    rec_df['GRUPO'] = rec_df['NATUREZA DA RECEITA'] + ' ' + rec_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS']
    ementario_df['GRUPO'] = ementario_df['NATUREZA DA RECEITA'] + ' ' + ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS']

    rec_df['ORIGEM'] = 'REC'
    ementario_df['ORIGEM'] = 'EMENTARIO'


    comparacao_df = pd.merge(rec_df[['GRUPO', 'NATUREZA DA RECEITA', 'ESPECIFICAÇÃO DA FONTE DE RECURSOS', 'ORIGEM']],
                             ementario_df[['GRUPO', 'NATUREZA DA RECEITA', 'ESPECIFICAÇÃO DA FONTE DE RECURSOS', 'ORIGEM']],
                             on='GRUPO', how='left', suffixes=('_REC', '_EMENTARIO'))

    comparacao_df = comparacao_df.drop_duplicates()

    incorretos_df = comparacao_df[comparacao_df['ORIGEM_EMENTARIO'].isna()]

    for idx, row in incorretos_df.iterrows():
        natureza_receita = row['NATUREZA DA RECEITA_REC']

    
        fonte_origem = ementario_df[(ementario_df['NATUREZA DA RECEITA'] == natureza_receita) &
                                    (ementario_df['ESPECIFICAÇÃO DA FONTE DE RECURSOS'] == 'Fonte de Origem')]

        if not fonte_origem.empty:
            incorretos_df.at[idx, 'ESPECIFICAÇÃO DA FONTE DE RECURSOS_REC'] = 'Fonte de Origem'
            incorretos_df.at[idx, 'GRUPO'] = natureza_receita + ' Fonte de Origem'

    corretos_df = comparacao_df.dropna(subset=['ORIGEM_EMENTARIO'])

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        output_file = tmp.name
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            comparacao_df.to_excel(writer, sheet_name='Comparacao Completa', index=False)
            corretos_df.to_excel(writer, sheet_name='Corretos', index=False)
            incorretos_df.to_excel(writer, sheet_name='Incorretos', index=False)

    return output_file

def main():
    st.title("REC VS Ementário da Receita")
    


    ementario_file = st.file_uploader("Selecione o arquivo do Ementário da Receita", type="xlsx")
    rec_file = st.file_uploader("Selecione o arquivo REC", type="xlsx")

    if ementario_file and rec_file:
        if st.button("Processar Arquivos"):

            output_file = processar_arquivos(ementario_file, rec_file)

            st.success("Arquivo gerado com sucesso!")
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Baixar o arquivo",
                    data=file,
                    file_name="resultado_REC_EmentarioDaReceira.xlsx"
                )

if __name__ == "__main__":
    main()
