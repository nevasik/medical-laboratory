from fpdf import FPDF
import csv
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_pdf(self, data, patient_info):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)


        pdf.set_font_size(16)
        pdf.cell(200, 10, txt="Отчет о лабораторном анализе", ln=1, align='C')
        pdf.ln(10)

        pdf.set_font_size(12)
        pdf.cell(200, 6, txt=f"Пациент: {patient_info['name']}", ln=1)
        pdf.cell(200, 6, txt=f"Возраст: {patient_info['age']}", ln=1)
        pdf.cell(200, 6, txt=f"Доктор: {patient_info['doctor']}", ln=1)
        pdf.ln(10)


        self._create_results_table(pdf, data)


        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, 'C')

        filename = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(name=str(filename))
        return filename

    def _create_results_table(self, pdf, data):
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(80, 10, 'Test Name', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'Result', 1, 0, 'C', 1)
        pdf.cell(60, 10, 'Reference Range', 1, 1, 'C', 1)

        pdf.set_fill_color(255, 255, 255)
        for row in data:
            pdf.cell(80, 10, row['test_name'], 1, 0, 'L', 1)
            pdf.cell(50, 10, str(row['result']), 1, 0, 'C', 1)
            pdf.cell(60, 10, row['reference_range'], 1, 1, 'C', 1)

    def generate_csv(self, data, patient_info):
        filename = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Patient Name", "Age", "Doctor"])
            writer.writerow([patient_info['name'], patient_info['age'], patient_info['doctor']])
            writer.writerow([])
            writer.writerow(["Test Name", "Result", "Reference Range"])
            for row in data:
                writer.writerow([row['test_name'], row['result'], row['reference_range']])
        return filename