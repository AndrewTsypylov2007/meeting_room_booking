from datetime import date
from sqlalchemy import ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.rooms import Room, TimeSlot
from src.models.users import User
from src.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    
    slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id", ondelete="CASCADE"), nullable=False)
    
    booking_date: Mapped[date] = mapped_column(Date, nullable=False) 

    user: Mapped["User"] = relationship()
    
    room: Mapped["Room"] = relationship()
    
    slot: Mapped["TimeSlot"] = relationship()

    __table_args__ = (
        UniqueConstraint("room_id", "slot_id", "booking_date", name="uq_room_slot_date"),
    )
