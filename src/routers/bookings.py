from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.users import User, UserRole
from src.schemas.bookings import RoomWithSlotsResponse, BookingCreate, BookingResponse
from src.auth.dependencies import get_current_user
from src.crud.bookings import (
    get_rooms_with_slot_status,
    create_booking,
    get_booking_by_id,
    delete_booking_by_id,
)

router = APIRouter(prefix="/bookings", tags=["Бронирование"])

@router.get("/rooms", response_model=list[RoomWithSlotsResponse])
async def get_rooms_availability(
    target_date: date,  
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_rooms_with_slot_status(db, booking_date=target_date)



@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def make_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_booking = await create_booking(db, booking_in=booking_in, user_id=current_user.id)
    
    if new_booking is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот временной слот на выбранную дату уже занят!"
        )
    return new_booking
@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy.future import select
    from src.models.bookings import Booking
    
    query = select(Booking).where(Booking.slot_id == slot_id)
    result = await db.execute(query)
    booking = result.scalars().first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование на этот слот не найдено"
        )
    if current_user.role != UserRole.ADMIN and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Вы можете отменять только свои бронирования."
        )
    
    await delete_booking_by_id(db, booking=booking)
    return None

