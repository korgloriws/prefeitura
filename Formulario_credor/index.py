import xlwings as xw
import pandas as pd
import os
import shutil

def brazilian_formatter(x):
    s = str(int(x * 100))  
    if len(s) <= 2:
        return f"0,{s.zfill(2)}"
    else:
        int_part = s[:-2]
        decimal_part = s[-2:]
        int_part_with_dot = f"{int(int_part):,}".replace(",", ".")
        return f"{int_part_with_dot},{decimal_part}"

def fill_and_save_form(group, name, payment_month, payment_date, template_file, output_folder):
    try:
        output_file_name = f'Preenchido_{name}_Anexo_V - Comprovante de Retenção.xlsx'
        output_file_path = os.path.join(output_folder, output_file_name)
        shutil.copy(template_file, output_file_path)

        wb = xw.Book(output_file_path)
        ws = wb.sheets['Plan1']

        ws.range('A9').value = group['cpf_cnpj'].iloc[0]
        ws.range('D9').value = name
        ws.range('F11').value = payment_month
        ws.range('D40').value = payment_date  
        ws.range('A40').value = "Hemerson Fernandes Soares"

        start_row = 12
        group_sum = group.groupby('Código de receita').sum().reset_index()

        for i, (_, row) in enumerate(group_sum.iterrows()):
            row_number = start_row + i
            ws.range(f'C{row_number}').value = row['Código de receita']
            ws.range(f'E{row_number}').value = brazilian_formatter(row['valor_bruto'])
            ws.range(f'G{row_number}').value = brazilian_formatter(row['valor_des'])
            ws.range(f'A{row_number}').value = payment_month

        wb.save()
        wb.close()
    except Exception as e:
        print(f"Failed to process group {name}. Error: {e}")

if __name__ == "__main__":
    output_folder = 'output_forms'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    payment_month = input("Por favor, insira o mês de pagamento: ")
    payment_date = input("Por favor, insira a data do pagamento (dd/mm/aaaa): ")  

    source_file_path = 'RELATÓRIO 979 - IRRF(4) Final após ajustes.xls'
    source_df = pd.read_excel(source_file_path)
    filtered_source_df = source_df[["credor", "cpf_cnpj", "valor_bruto", "valor_des", "Código de receita"]]
    grouped = filtered_source_df.groupby("credor")
    template_file = 'Anexo_V - Comprovante de Retenção (1).xlsx'

    for i, (name, group) in enumerate(grouped):
        print(f"Processing group {i+1}/{len(grouped)}: {name}")
        group = group.reset_index(drop=True)
        fill_and_save_form(group, name, payment_month, payment_date, template_file, output_folder)  

