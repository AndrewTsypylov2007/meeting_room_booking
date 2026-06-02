from sqlalchemy import String, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=500), nullable=True)
    slots: Mapped[list["TimeSlot"]] = relationship(back_populates="room", cascade="all, delete-orphan")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    room: Mapped["Room"] = relationship(back_populates="slots")
