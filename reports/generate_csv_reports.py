import csv

from reports.report import invoice_data


def generate_csv_report(invoice_data):
    with open("invoice_report.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Patient Name", "Insurance Company", "Period", "Service Code", "Service Cost", "Total Cost"])

        for record in invoice_data:
            for service in record['services']:
                writer.writerow(
                    [record['patient_name'], record['insurance_company'], record['period'], service['service_code'],
                     service['cost'], record['total_cost']])


# Пример использования
generate_csv_report(invoice_data)
