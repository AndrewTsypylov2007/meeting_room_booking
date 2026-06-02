# 🏢 Сервис автоматизации бронирования переговорных комнат

Проект представляет собой fullstack-приложение для автоматизации распределения временных слотов в коворкинге. Сервис решает проблему наложения встреч (double-booking), обеспечивает прозрачность графика занятости комнат и реализует строгое разграничение прав доступа между сотрудниками и администраторами.

## 🛠️ Технологический стек
*   **Бэкенд**: Python 3.12 + FastAPI (Async)
*   **База данных**: PostgreSQL + SQLAlchemy 2.0 (асинхронный драйвер `asyncpg`)
*   **Управление зависимостями**: Poetry
*   **Тестирование**: Pytest + Httpx (Async)
*   **Контейнеризация**: Docker + Docker Compose
*   **Фронтенд-интерфейс**: Jinja2 + Tailwind CSS (SPA-дашборд)

---

## 🚀 Инструкция по локальному запуску

### Вариант 1. Запуск через Docker Compose (Рекомендуемый, одной командой)
Убедитесь, что у вас запущен Docker Desktop, и выполните в корне проекта:
```bash
docker-compose up --build -d
```
Приложение автоматически развернет базу данных PostgreSQL на порту `5433` и веб-сервер на порту `8000`. При первом старте база автоматически наполнится тестовыми комнатами и обязательными слотами из ТЗ.

*   **Главная страница (Интерфейс)**: [http://localhost:8000/](http://localhost:8000/)
*   **Интерактивная документация API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Вариант 2. Локальный запуск (Разработка и отладка)
1. Установите зависимости проекта через Poetry:
   ```bash
   poetry install
   ```
2. Запустите только контейнер базы данных:
   ```bash
   docker-compose up db -d
   ```
3. Запустите сервер FastAPI из корня проекта:
   ```bash
   # Для Windows PowerShell:
   \$env:PYTHONPATH="."
   poetry run uvicorn src.main:app --reload

   # Для Windows CMD:
   set PYTHONPATH=.
   poetry run uvicorn src.main:app --reload
   ```

---

## 🧪 Запуск автоматических тестов (`pytest`)

В проекте написаны интеграционные асинхронные тесты, проверяющие сквозной сценарий регистрации пользователя, генерацию и валидацию JWT-токенов в изолированной тестовой среде PostgreSQL.

Для запуска тестов выполните:
```bash
# Для Windows PowerShell:
\$env:PYTHONPATH="."
poetry run pytest -W ignore

# Для Windows CMD:
set PYTHONPATH=.
poetry run pytest -W ignore
```

---

## 🔑 Учетные данные для демонстрации (Тест ролей)

Вы можете зарегистрировать аккаунты прямо через вкладку «Регистрация» на главном экране приложения. Для проверки изоляции данных заложен следующий алгоритм:

1.  **Аккаунт сотрудника**: `user@shift.ru` (Пароль: `employee123`) — имеет право просматривать расписание, бронировать свободные слоты и отменять **только свои** бронирования. При попытке отменить чужую бронь получит ошибку `403 Forbidden`.
2.  **Аккаунт администратора**: `admin@shift.ru` (Пароль: `admin123`) — система автоматически распознает роль `admin` по ключевому слову в email, перекрашивает дашборд и открывает доступ к **отмене абсолютно любого бронирования** в коворкинге.

---

## 📡 Примеры работы REST API (Примеры cURL запросов)

### 1. Регистрация сотрудника
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@shift.ru",
  "password": "employee123"
}'
```

### 2. Аутентификация (Получение JWT-токена)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@shift.ru&password=employee123'
```

### 3. Просмотр доступности комнат на дату (Требуется Токен)
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/bookings/rooms?target_date=2026-06-03' \
  -H 'Authorization: Bearer ВАШ_JWT_ТОКЕН'
```

### 4. Создание бронирования
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/bookings' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ВАШ_JWT_ТОКЕН' \
  -d '{
  "room_id": 1,
  "slot_id": 2,
  "date": "2026-06-03"
}'
```

---

## 📂 Слоистая архитектура проекта (Clean Architecture)
Код строго разделен на изолированные слои ответственности:
*   `src/models/` — ORM-модели SQLAlchemy (схемы таблиц базы данных).
*   `src/schemas/` — Валидаторы входных и выходных данных Pydantic.
*   `src/crud/` — Изолированные асинхронные SQL-запросы к СУБД.
*   `src/routers/` — Контроллеры HTTP-эндпоинтов REST API.
*   `src/auth/` — Логика хеширования паролей (`bcrypt`) и генерации JWT.
*   `templates/` — HTML/JS SPA-интерфейс дашборда на Jinja2.
