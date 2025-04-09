import sys

from PyQt6.QtWidgets import (QApplication)

from core.config.config import get_config
from core.database.db import get_connection_db, seed_basic_data, seed_quality_data
from GUI.qt.main_window  import MainWindow


def main():
    conn = None
    try:
        cfg = get_config()
        conn = get_connection_db(cfg['mysql'])

        print("Generating test data...")
        seed_basic_data(conn)
        seed_quality_data(conn, 50)
        print("Done! Test data created.")

        app = QApplication(sys.argv)
        window = MainWindow(conn)
        window.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.close()
        exit(1)


if __name__ == "__main__":
    main()
