from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.users import User, UserRole
from src.schemas.auth import UserCreate
from src.auth.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate, is_admin: bool = False) -> User:
    hashed_password = get_password_hash(user_in.password)
    role = UserRole.ADMIN if is_admin else UserRole.EMPLOYEE

    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)  
    
    return db_user
