import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"), 
        default=UserRole.EMPLOYEE, 
        nullable=False
    )
