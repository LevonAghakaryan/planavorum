from sqlalchemy.orm import Session
from app.repositories.table import TableRepository
from app.repositories.guest_members import GuestMemberRepository
from app.schemas.table import TableCreate, TableBulkPositionUpdate
from fastapi import HTTPException


class TableService:
    def __init__(self, db: Session):
        self.table_repo = TableRepository(db)
        self.member_repo = GuestMemberRepository(db)

    def create_table(self, table_data: TableCreate):
        return self.table_repo.create(table_data)

    def get_wedding_tables(self, wedding_id: int):
        return self.table_repo.get_by_wedding(wedding_id)

    def get_table_available_seats(self, table_id: int) -> int:
        table = self.table_repo.get_by_id(table_id)
        if not table:
            return 0
        seated_count = self.member_repo.count_seated_at_table(table_id)
        return table.capacity - seated_count

    def update_capacity(self, table_id: int, capacity: int):
        if capacity < 1:
            raise HTTPException(status_code=400, detail="Capacity must be at least 1")
        seated = self.member_repo.count_seated_at_table(table_id)
        if capacity < seated:
            raise HTTPException(
                status_code=400,
                detail=f"Չի կարելի կրճատել. արդեն {seated} հոգի նստած է այս սեղանի մոտ։"
            )
        table = self.table_repo.update_capacity(table_id, capacity)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return table

    def update_position(self, table_id: int, x_pos: float, y_pos: float):
        table = self.table_repo.update_position(table_id, x_pos, y_pos)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return table

    def delete_table(self, table_id: int):
        return self.table_repo.delete(table_id)

    def update_bulk_positions(self, wedding_id: int, payload: TableBulkPositionUpdate) -> int:
        updated = 0
        for item in payload.positions:
            db_table = self.table_repo.get_by_id(item.table_id)
            # Security: ստուգել որ սեղանը հենց այս հարսանիքինն է
            if db_table and db_table.wedding_id == wedding_id:
                db_table.x_pos = item.x_pos
                db_table.y_pos = item.y_pos
                updated += 1
        self.table_repo.db.commit()
        return updated