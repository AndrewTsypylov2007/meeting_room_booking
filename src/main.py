from contextlib import asynccontextmanager
from datetime import time
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select

from src.database import engine, Base, async_session_maker
from src.models.rooms import Room, TimeSlot
from src.routers.auth import router as auth_router
from src.routers.bookings import router as bookings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        rooms_check = await session.execute(select(Room))
        if not rooms_check.scalars().first():
            room1 = Room(name="Большая переговорная", description="Зал с проектором и флипчартом на 10 человек")
            session.add(room1)
            await session.flush()
            slot1 = TimeSlot(room_id=room1.id, start_time=time(9, 0), end_time=time(11, 0))
            slot2 = TimeSlot(room_id=room1.id, start_time=time(13, 0), end_time=time(16, 0))
            room2 = Room(name="Малая переговорная (Sky Room)", description="Уютная локация для быстрых созвонов на 3 человека")
            session.add(room2)
            await session.flush()
            
            slot3 = TimeSlot(room_id=room2.id, start_time=time(10, 0), end_time=time(12, 0))
            slot4 = TimeSlot(room_id=room2.id, start_time=time(14, 0), end_time=time(15, 30))
            
            session.add_all([slot1, slot2, slot3, slot4])
            await session.commit()
    yield

app = FastAPI(
    title="Сервис бронирования переговорных комнат",
    version="1.0.0",
    lifespan=lifespan
)

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
