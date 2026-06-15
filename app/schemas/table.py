from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional
from typing import List

class TableBase(BaseModel):
    table_number: str
    category: Literal['presidium', 'rectangle', 'double_rectangle', 'round']
    capacity: int = Field(..., gt=0, description="Աթոռների քանակը պետք է մեծ լինի 0-ից")
    side: Literal['bride', 'groom', 'mutual'] = 'mutual'


# Ստեղծելու համար
class TableCreate(TableBase):
    wedding_id: int


# Դիրքի թարմացում
class TablePositionUpdate(BaseModel):
    x_pos: float
    y_pos: float

class TableBulkPositionItem(BaseModel):
    table_id: int
    x_pos: float
    y_pos: float

class TableBulkPositionUpdate(BaseModel):
    positions: List[TableBulkPositionItem]

# Պատասխանի (Response) համար
class TableResponse(TableBase):
    id: int
    wedding_id: int
    x_pos: Optional[float] = None
    y_pos: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True