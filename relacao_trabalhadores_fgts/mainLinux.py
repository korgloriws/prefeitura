import streamlit as st
import pdfplumber
import pandas as pd

def extract_worker_names(pdf_path):
    worker_names = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                header = table[0]
                if "Nome Trabalhador" in header:
                    col_index = header.index("Nome Trabalhador")
                    for row in table[1:]:
                        if len(row) > col_index:
                            worker_names.append(row[col_index])
    return worker_names

def main():
    st.title("Relação de Trabalhadores FGTS")

    uploaded_file = st.file_uploader("Faça upload do arquivo PDF", type="pdf")

    if uploaded_file is not None:
        names = extract_worker_names(uploaded_file)

        st.write("Nomes dos Trabalhadores:")
        st.write(names)

        df = pd.DataFrame(names, columns=["Nome Trabalhador"])

        @st.cache_data
        def convert_df_to_excel(df):
            from io import BytesIO
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return output

        xlsx_data = convert_df_to_excel(df)
        st.download_button(
            label="Baixar resultado em XLSX",
            data=xlsx_data,
            file_name="nomes_trabalhadores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
