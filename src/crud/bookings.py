from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.rooms import Room, TimeSlot
from src.models.bookings import Booking
from src.schemas.bookings import BookingCreate, RoomWithSlotsResponse, SlotResponse

# 1. Получить все комнаты и статус их слотов на конкретную дату
async def get_rooms_with_slot_status(db: AsyncSession, booking_date: date) -> list[RoomWithSlotsResponse]:
    # Загружаем все комнаты вместе с их временными слотами
    rooms_query = select(Room).options(selectinload(Room.slots))
    rooms_result = await db.execute(rooms_query)
    rooms = rooms_result.scalars().all()

    # Ищем id слотов, которые уже заняты на эту дату
    bookings_query = select(Booking.slot_id).where(Booking.booking_date == booking_date)
    bookings_result = await db.execute(bookings_query)
    occupied_slot_ids = set(bookings_result.scalars().all())

    result = []
    for room in rooms:
        slots_data = []
        for slot in room.slots:
            is_free = slot.id not in occupied_slot_ids
            slots_data.append(
                SlotResponse(
                    id=slot.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    is_free=is_free
                )
            )
        
        result.append(
            RoomWithSlotsResponse(
                id=room.id,
                name=room.name,
                description=room.description,
                slots=slots_data
            )
        )
    return result

# 2. Создать новое бронирование (с проверкой на занятость)
async def create_booking(db: AsyncSession, booking_in: BookingCreate, user_id: int) -> Booking | None:
    # Проверяем, свободен ли слот на эту дату
    check_query = select(Booking).where(
        Booking.room_id == booking_in.room_id,
        Booking.slot_id == booking_in.slot_id,
        Booking.booking_date == booking_in.date
    )
    check_result = await db.execute(check_query)
    if check_result.scalars().first():
        return None  # Слот уже занят

    # Если всё свободно — создаем запись бронирования
    db_booking = Booking(
        user_id=user_id,
        room_id=booking_in.room_id,
        slot_id=booking_in.slot_id,
        booking_date=booking_in.date
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking

# 3. Найти бронирование по его ID
async def get_booking_by_id(db: AsyncSession, booking_id: int) -> Booking | None:
    query = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(query)
    return result.scalars().first()

# 4. Удалить бронирование из базы данных
async def delete_booking_by_id(db: AsyncSession, booking: Booking) -> None:
    await db.delete(booking)
    await db.commit()
