from fpdf import FPDF
import datetime
import os
from constants import SERVICES


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        self.add_font('Arial', '', os.path.join(font_dir, 'arial.ttf'), uni=True)
        self.add_font('Arial', 'B', os.path.join(font_dir, 'arialbd.ttf'), uni=True)
        self.set_font('Arial', size=12)


def generate_pdf_report(patient_id, services, save_path=""):
    try:
        # Создаем директорию для отчетов
        if save_path:
            os.makedirs(save_path, exist_ok=True)

        pdf = PDF()
        pdf.add_page()

        # Заголовок
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Отчет о результатах анализа', 0, 1, 'C')
        pdf.ln(10)

        # Информация о пациенте
        patient_id_str = str(patient_id)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Пациент: {patient_id_str}', 0, 1)
        pdf.cell(0, 10, f'Дата: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1)
        pdf.ln(10)

        # Таблица
        pdf.set_fill_color(200, 220, 255)
        col_widths = [120, 40, 30]
        headers = ['Исследование', 'Результат', 'Стоимость']

        # Заголовки таблицы
        pdf.set_font('Arial', 'B', 12)
        for width, header in zip(col_widths, headers):
            pdf.cell(width, 10, header, 1, 0, 'C', fill=True)
        pdf.ln()

        # Данные таблицы
        pdf.set_font('Arial', '', 12)
        total = 0
        for service in services:
            # Обработка кода услуги
            try:
                code = int(str(service.get('code', 0)).__trunc__()
            except:
                code = 0

            # Обработка результата
            result = f"{service.get('result', 'N/A')}"

            # Поиск названия услуги
            name = f'Услуга {code}'
            for s in SERVICES:
                try:
                    if int(s['code']) == code:
                        name = str(s['name'])
                        break
                except:
                    continue

            # Стоимость
            try:
                cost = float(262.71)
            except:
                cost = 0.0
            total += cost

            # Формирование строки
            row_data = [
                f'{name} ({code})',
                f'{result}',
                f'{cost:.2f} ₽'
            ]

            # Добавление строки в таблицу
            for width, text in zip(col_widths, row_data):
                pdf.cell(width, 10, text, 1)
            pdf.ln()

        # Итог
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Итого к оплате: {total:.2f} ₽', 0, 1, 'R')

        # Сохранение файла
        filename = f'report_{patient_id_str}.pdf'
        full_path = os.path.join(save_path, filename) if save_path else filename
        pdf.output(full_path)
        print(f'✅ Отчет сохранен: {full_path}')

    except Exception as e:
        print(f'❌ Ошибка генерации: {type(e).__name__}: {str(e)}')
        raise