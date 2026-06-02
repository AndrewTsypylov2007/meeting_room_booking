from datetime import date, time
from pydantic import BaseModel
from src.models.users import UserRole

class SlotResponse(BaseModel):
    id: int
    start_time: time
    end_time: time
    is_free: bool 

    model_config = {"from_attributes": True}

class RoomWithSlotsResponse(BaseModel):
    id: int
    name: str
    description: str | None
    slots: list[SlotResponse]

    model_config = {"from_attributes": True}


class BookingCreate(BaseModel):
    room_id: int
    slot_id: int
    date: date 
class BookingResponse(BaseModel):
    id: int
    room_id: int
    slot_id: int
    user_id: int
    date: date

    model_config = {"from_attributes": True}
