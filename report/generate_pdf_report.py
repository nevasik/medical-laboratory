# report/generate_pdf_report.py
from fpdf import FPDF
import datetime
import os
from constants import SERVICES


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        try:
            # Получаем абсолютный путь до шрифтов
            font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
            arial_path = os.path.join(font_dir, 'arial.ttf')
            arialbd_path = os.path.join(font_dir, 'arialbd.ttf')

            if not os.path.exists(arial_path):
                raise FileNotFoundError(f"Font file not found: {arial_path}")

            self.add_font('Arial', '', arial_path, uni=True)
            self.add_font('Arial', 'B', arialbd_path, uni=True)
            self.set_font('Arial', size=12)
        except Exception as e:
            print(f"❌ Ошибка загрузки шрифтов: {str(e)}")
            raise

def generate_pdf_report(patient_id, services, save_path=""):
    try:
        # Создаем директорию для отчетов
        os.makedirs(save_path, exist_ok=True) if save_path else None

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Заголовок
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Отчет о результатах анализа', 0, 1, 'C')
        pdf.ln(10)

        # Информация о пациенте
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Пациент: {patient_id}', 0, 1)
        pdf.cell(0, 10, f'Дата: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1)
        pdf.ln(10)

        # Таблица с результатами
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(120, 10, 'Исследование', 1, 0, 'C', fill=True)
        pdf.cell(40, 10, 'Результат', 1, 0, 'C', fill=True)
        pdf.cell(30, 10, 'Стоимость', 1, 1, 'C', fill=True)

        total = 0
        for service in services:
            code = service['code']
            name = next((s['name'] for s in SERVICES if s['code'] == code), f'Услуга {code}')
            result = str(service['result'])
            cost = 262.71
            total += cost

            pdf.cell(120, 10, f'{name} ({code})', 1)
            pdf.cell(40, 10, result, 1)
            pdf.cell(30, 10, f'{cost:.2f} ₽', 1, 1)

        # Итоговая сумма
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Итого к оплате: {total:.2f} ₽', 0, 1, 'R')

        # Сохранение файла
        filename = f'report_{patient_id}.pdf'
        full_path = os.path.join(save_path, filename) if save_path else filename
        pdf.output(full_path)
        print(f'✅ Отчет сохранен: {full_path}')

    except Exception as e:
        print(f'❌ Ошибка генерации: {str(e)}')
        raise