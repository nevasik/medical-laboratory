from PyQt6.QtGui import QColor

# Основные цвета
PRIMARY_COLOR = "#497C51"  # RGB(73, 140, 81)
SECONDARY_COLOR = "#76E383"  # RGB(118, 227, 131)
BACKGROUND_COLOR = "#FFFFFF"  # Белый
TEXT_COLOR = "#000000"  # Черный
ERROR_COLOR = "#F44336"
SUCCESS_COLOR = "#4CAF50"

# Стили для основного окна
MAIN_WINDOW_STYLE = f"""
    QDialog {{
        background-color: {BACKGROUND_COLOR};
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
"""

# Стили для кнопок
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {SECONDARY_COLOR};
        color: {TEXT_COLOR};
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 5px;
        padding: 8px;
        min-width: 100px;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
"""

# Стиль для основной кнопки
PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 5px;
        padding: 8px;
        min-width: 100px;
        font-family: "Comic Sans MS";
        font-size: 12pt;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {SECONDARY_COLOR};
        color: {TEXT_COLOR};
    }}
"""

# Стили для полей ввода
INPUT_STYLE = f"""
    QLineEdit {{
        background-color: white;
        border: 2px solid {SECONDARY_COLOR};
        border-radius: 5px;
        padding: 5px;
        color: {TEXT_COLOR};
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
    QLineEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
"""

# Стили для меток
LABEL_STYLE = f"""
    QLabel {{
        color: {TEXT_COLOR};
        font-weight: bold;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
"""

# Стили для выпадающих списков
COMBOBOX_STYLE = f"""
    QComboBox {{
        background-color: white;
        border: 2px solid {SECONDARY_COLOR};
        border-radius: 5px;
        padding: 5px;
        color: {TEXT_COLOR};
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
    QComboBox:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(down_arrow.png);
        width: 12px;
        height: 12px;
    }}
"""

# Стили для таблиц
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: white;
        border: 2px solid {SECONDARY_COLOR};
        border-radius: 5px;
        gridline-color: {SECONDARY_COLOR};
        font-family: "Comic Sans MS";
        font-size: 12pt;
        color: {TEXT_COLOR};
    }}
    QTableWidget::item {{
        padding: 5px;
        color: {TEXT_COLOR};
    }}
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 5px;
        border: none;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
"""

# Стили для сообщений об ошибках
ERROR_LABEL_STYLE = f"""
    QLabel {{
        color: {ERROR_COLOR};
        font-weight: bold;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
"""

# Стили для сообщений об успехе
SUCCESS_LABEL_STYLE = f"""
    QLabel {{
        color: {SUCCESS_COLOR};
        font-weight: bold;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
"""

# Стили для диалоговых окон с предупреждениями
WARNING_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {BACKGROUND_COLOR};
        border: 2px solid {SECONDARY_COLOR};
        border-radius: 5px;
    }}
    QLabel {{
        color: {TEXT_COLOR};
        font-weight: bold;
        font-family: "Comic Sans MS";
        font-size: 12pt;
        padding: 10px;
    }}
    QPushButton {{
        background-color: {SECONDARY_COLOR};
        color: {TEXT_COLOR};
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 5px;
        padding: 8px;
        min-width: 100px;
        font-family: "Comic Sans MS";
        font-size: 12pt;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
"""