# README: Медицинский сервис обработки анализов

## 📌 Описание проекта

Данный проект представляет собой систему автоматизации работы медицинских лабораторий. Включает в себя:

- 📡 **FastAPI backend** для обработки данных и взаимодействия с БД (MySQL)
- 🔄 **WebSocket-сервер** для обновления статусов анализов в реальном времени
- 📊 **Генерацию отчетов в форматах CSV и PDF**
- 🖥️ **Клиентскую часть (React)** для отображения данных и взаимодействия с пользователем

---

## 🚀 Установка и запуск

### 🔧 1. Установка зависимостей

Для работы потребуется Python 3.9+ и Node.js 16+.

#### 📜 Backend:

1. Установите виртуальное окружение (опционально):
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/macOS
   venv\Scripts\activate  # для Windows
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```


### 📂 2. Настройка базы данных (MySQL)

1. Установите MySQL, если не установлен.
2. Создайте базу данных:
   ```sql
   CREATE DATABASE medical_analysis;
   ```
3. Импортируйте схему базы данных:
   ```bash
   mysql -u root -p medical_analysis < schema.sql
   ```
4. В файле `config.py` укажите параметры подключения к БД:
   ```python
   DATABASE_URL = "mysql+pymysql://user:password@localhost/medical_analysis"
   ```

---

### ▶️ 3. Запуск сервера FastAPI

1. Запустите сервер FastAPI:
   ```bash
   uvicorn main:app --reload
   ```
2. Документация API доступна по адресу:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 📡 4. Запуск WebSocket

1. Подключитесь к WebSocket-серверу с помощью `websocat`:
   ```bash
   websocat ws://localhost:8000/ws/status
   ```
2. WebSocket автоматически обновляет статусы анализов при изменениях в базе данных.

---



## 📝 Генерация отчетов (CSV/PDF)

1. Для генерации CSV-отчета выполните:
   ```bash
   curl -X GET "http://localhost:8000/report/csv?insurance_company=X&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"
   ```
2. Для генерации PDF-отчета выполните:
   ```bash
   curl -X GET "http://localhost:8000/report/pdf?insurance_company=X&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"
   ```

Отчеты сохраняются в папке `reports/`.

---

## 📌 Итог

- ✅ **Настроили БД**
- ✅ **Запустили FastAPI backend**
- ✅ **Запустили WebSocket**
- ✅ **Генерация отчетов в CSV и PDF**

🎯 Всё готово к работе! 🚀

