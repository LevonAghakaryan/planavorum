from sqlalchemy.orm import Session, joinedload
from app.models.table import Table
from app.schemas.table import TableCreate
from typing import List, Optional


class TableRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, table_data: TableCreate) -> Table:
        db_table = Table(
            wedding_id=table_data.wedding_id,
            table_number=table_data.table_number,
            category=table_data.category,
            capacity=table_data.capacity,
            side=table_data.side,
        )
        self.db.add(db_table)
        self.db.commit()
        self.db.refresh(db_table)
        return db_table

    def get_by_wedding(self, wedding_id: int) -> List[Table]:
        return (
            self.db.query(Table)
            .options(joinedload(Table.members))
            .filter(Table.wedding_id == wedding_id)
            .all()
        )

    def get_by_id(self, table_id: int) -> Optional[Table]:
        return (
            self.db.query(Table)
            .options(joinedload(Table.members))
            .filter(Table.id == table_id)
            .first()
        )

    def update_capacity(self, table_id: int, capacity: int) -> Optional[Table]:
        db_table = self.get_by_id(table_id)
        if db_table:
            db_table.capacity = capacity
            self.db.commit()
            self.db.refresh(db_table)
        return db_table

    def update_table_number(self, table_id: int, table_number: str) -> Optional[Table]:
        db_table = self.get_by_id(table_id)
        if db_table:
            db_table.table_number = table_number
            self.db.commit()
            self.db.refresh(db_table)
        return db_table

    def update_position(self, table_id: int, x_pos: float, y_pos: float) -> Optional[Table]:
        db_table = self.get_by_id(table_id)
        if db_table:
            db_table.x_pos = x_pos
            db_table.y_pos = y_pos
            self.db.commit()
            self.db.refresh(db_table)
        return db_table

    def delete(self, table_id: int) -> bool:
        db_table = self.get_by_id(table_id)
        if db_table:
            self.db.delete(db_table)
            self.db.commit()
            return True
        return False