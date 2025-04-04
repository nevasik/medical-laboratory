from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex

class HistoryModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.headers = ["Время", "Логин", "Статус", "Роль"]
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            return self._format_row(row)[index.column()]

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

    def _format_row(self, row):
        time, login, success, role = row
        return [
            time.strftime("%Y-%m-%d %H:%M:%S"),
            login,
            "Успешно" if success else "Ошибка",
            role or "Неизвестно"
        ]