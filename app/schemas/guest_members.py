from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GuestMemberBase(BaseModel):
    first_name: Optional[str] = None
    table_id: Optional[int] = None
    seat_index: Optional[int] = None  # ✅ Նոր


class GuestMemberUpdate(BaseModel):
    first_name: Optional[str] = None
    table_id: Optional[int] = None
    seat_index: Optional[int] = None  # ✅ Նոր


class GuestMemberResponse(GuestMemberBase):
    id: int
    guest_id: int
    created_at: datetime

    class Config:
        from_attributes = True