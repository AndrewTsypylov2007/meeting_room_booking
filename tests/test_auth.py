import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.database import Base, get_db
from src.main import app

# Явно импортируем модели, чтобы SQLAlchemy увидела их чертежи
import src.models.users
import src.models.rooms
import src.models.bookings

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5433/booking_test"
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)

@pytest.mark.asyncio(loop_scope="session")
async def test_register_and_login():
    # 1. Сначала жестко зачищаем и создаем таблицы прямо перед тестом
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 2. Открываем соединение и изолированную транзакцию
    async with engine_test.connect() as connection:
        transaction = await connection.begin()
        async_session = AsyncSession(bind=connection, expire_on_commit=False)

        # 3. Подменяем зависимость get_db для FastAPI на нашу чистую сессию
        app.dependency_overrides[get_db] = lambda: async_session

        # 4. Открываем клиент для отправки запросов
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            
            # --- ТЕСТ 1: Регистрация нового сотрудника ---
            response = await client.post("/api/v1/auth/register", json={
                "email": "test_user@example.com",
                "password": "secretpassword123"
            })
            assert response.status_code == 201
            assert response.json()["email"] == "test_user@example.com"

            # --- ТЕСТ 2: Вход по логину/паролю и получение токена ---
            login_response = await client.post("/api/v1/auth/login", data={
                "username": "test_user@example.com",
                "password": "secretpassword123"
            })
            assert login_response.status_code == 200
            assert "access_token" in login_response.json()

        # 5. Очищаем глобальное состояние после теста
        app.dependency_overrides.clear()
        await async_session.close()
        await transaction.rollback()
