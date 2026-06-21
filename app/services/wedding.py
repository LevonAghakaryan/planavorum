from sqlalchemy.orm import Session
from typing import List

from app.repositories.wedding import WeddingRepository
from app.schemas.wedding import WeddingCreate


class WeddingService:
    def __init__(self, db: Session):
        self.wedding_repo = WeddingRepository(db)

    def create_wedding(self, wedding_data: WeddingCreate):
        return self.wedding_repo.create(wedding_data)

    def get_all_weddings(self) -> List:
        return self.wedding_repo.get_all()

    def get_wedding(self, wedding_id: int):
        return self.wedding_repo.get_by_id(wedding_id)

    def update_title(self, wedding_id: int, new_title: str):
        return self.wedding_repo.update_title(wedding_id, new_title)

    def delete_wedding(self, wedding_id: int) -> bool:
        return self.wedding_repo.delete(wedding_id)