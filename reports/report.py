from fpdf import FPDF


def generate_pdf_report(invoice_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Invoice for Insurance Company", ln=True, align="C")

    for record in invoice_data:
        pdf.cell(200, 10, txt=f"Patient: {record['patient_name']}", ln=True)
        pdf.cell(200, 10, txt=f"Insurance Company: {record['insurance_company']}", ln=True)
        pdf.cell(200, 10, txt=f"Period: {record['period']}", ln=True)
        pdf.cell(200, 10, txt=f"Total Cost: {record['total_cost']}", ln=True)

        for service in record['services']:
            pdf.cell(200, 10, txt=f"Service Code: {service['service_code']}, Cost: {service['cost']}", ln=True)

        pdf.ln(10)  # Add some space between records

    pdf.output("invoice_report.pdf")


# Пример использования
invoice_data = [
    {
        "patient_name": "John Doe",
        "insurance_company": "ABC Insurance",
        "period": "01/2025 - 03/2025",
        "total_cost": 1234.56,
        "services": [
            {"service_code": 619, "cost": 200},
            {"service_code": 258, "cost": 300}
        ]
    }
]

generate_pdf_report(invoice_data)
