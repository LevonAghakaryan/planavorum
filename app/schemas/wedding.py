from pydantic import BaseModel
from datetime import datetime


class WeddingBase(BaseModel):
    title: str


class WeddingCreate(WeddingBase):
    pass


class WeddingResponse(WeddingBase):
    id:         int
    slug:       str
    token:      str
    created_at: datetime

    class Config:
        from_attributes = True