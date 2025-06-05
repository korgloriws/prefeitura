import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from textwrap import wrap


def main():
    pass

def generate_pdf(results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["BodyText"]
    module_style = styles["Heading3"]

    elements.append(Paragraph("Relatório de Validação", title_style))
    elements.append(Spacer(1, 12))
    
    count = 0 
    max_chars_per_line = 80  
    max_table_rows = 30 
    
    for result in results:
        match = re.match(r"(d\d+_\d+)", result)
        if match:
            modulo = match.group(1)
            elements.append(Paragraph(f"<b>{modulo}</b>", module_style))
            elements.append(Spacer(1, 6))
        
        background_color = colors.white
        if "alert-success" in result:
            msg = re.sub(r"<.*?>", "", result)
            background_color = colors.lightgreen
        elif "alert-warning" in result:
            msg = re.sub(r"<.*?>", "", result)
            background_color = colors.lightyellow
        elif "alert-danger" in result:
            msg = re.sub(r"<.*?>", "", result)
            background_color = colors.lightcoral
        else:
            msg = re.sub(r"<.*?>", "", result)
        
        wrapped_lines = wrap(msg, max_chars_per_line)
        table_data = [[Paragraph(line, normal_style)] for line in wrapped_lines]
        
        table = Table(table_data, colWidths=[500])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), background_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(KeepTogether([table, Spacer(1, 12)]))
        
        if "<table" in result:
            table_data = []
            rows = re.findall(r"<tr.*?>(.*?)</tr>", result, re.DOTALL)
            for row in rows:
                cols = re.findall(r"<td.*?>(.*?)</td>", row)
                if cols:
                    table_data.append(cols)

            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))
        
        count += 1
        if count % max_table_rows == 0:
            elements.append(PageBreak())
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    main()
