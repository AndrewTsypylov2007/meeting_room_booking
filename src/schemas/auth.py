from pydantic import BaseModel, EmailStr, Field
from src.models.users import UserRole

# 1. Схема для регистрации нового пользователя
class UserCreate(BaseModel):
    email: EmailStr  # Автоматически проверяет, что это реальный email (есть @, точка и т.д.)
    password: str = Field(min_length=6, max_length=50, description="Пароль от 6 до 50 символов")

# 2. Схема для безопасного возврата данных пользователя наружу (без пароля!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    # Включаем режим совместимости с ORM моделями SQLAlchemy
    model_config = {"from_attributes": True}

# 3. Схема, которую сервис возвращает при успешном входе (JWT токен)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
