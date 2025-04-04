from PyQt6.QtGui import QColor

COMMON_STYLE = """
    QWidget {
        font-family: "Comic Sans MS";
        font-size: 12pt;
        background-color: white;
        color: black;
    }
    QPushButton {
        background-color: %s;
        color: black;
        border: 2px solid %s;
        border-radius: 5px;
        padding: 8px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: %s;
        color: white;
    }
    QLineEdit, QComboBox, QTableView {
        border: 2px solid %s;
        border-radius: 5px;
        padding: 5px;
        color: black;
    }
    QHeaderView::section {
        background-color: %s;
        color: black;
        padding: 5px;
    }
    QLabel#title {
        color: %s;
        font-weight: bold;
        font-size: 14pt;
    }
""" % (
    QColor(118, 227, 131).name(),
    QColor(73, 140, 81).name(),
    QColor(73, 140, 81).name(),
    QColor(118, 227, 131).name(),
    QColor(118, 227, 131).name(),
    QColor(73, 140, 81).name()
)

LOGIN_EXTRA_STYLE = """
    QCheckBox { color: %s; }
    #captcha_label { border: 2px solid %s; }
""" % (
    QColor(73, 140, 81).name(),
    QColor(118, 227, 131).name()
)

MAIN_EXTRA_STYLE = """
    QLabel#user_info { 
        color: %s;
        font-size: 13pt;
    }
""" % QColor(73, 140, 81).name()