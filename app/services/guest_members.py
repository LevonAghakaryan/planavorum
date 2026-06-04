from sqlalchemy.orm import Session
from app.repositories.guest_members import GuestMemberRepository
from app.repositories.table import TableRepository
from fastapi import HTTPException
from typing import Optional


class GuestMemberService:
    def __init__(self, db: Session):
        self.member_repo = GuestMemberRepository(db)
        self.table_repo = TableRepository(db)

    def seat_member(self, member_id: int, table_id: Optional[int], seat_index: Optional[int] = None):
        if table_id is not None:
            table = self.table_repo.get_by_id(table_id)
            if not table:
                raise HTTPException(status_code=404, detail="Table not found")

            # ✅ Ստուգում ենք՝ կոնկրետ seat_index-ն արդեն զբաղված չէ
            if seat_index is not None:
                occupied = self.member_repo.get_by_table_and_seat(table_id, seat_index)
                if occupied and occupied.id != member_id:
                    raise HTTPException(status_code=400, detail="Այս ատոռն արդեն զբաղված է։")
            else:
                seated_count = self.member_repo.count_seated_at_table(table_id)
                if seated_count >= table.capacity:
                    raise HTTPException(status_code=400, detail="Այս սեղանի շուրջ ազատ աթոռ չկա։")

        return self.member_repo.update_seating(member_id, table_id, seat_index)

    def update_member_name(self, member_id: int, first_name: str):
        """Թույլ է տալիս անհատապես փոխել աթոռի վրայի անունը (Split-ից հետո խմբագրելու համար)"""
        return self.member_repo.update_name(member_id, first_name)

    def get_unseated_members(self, wedding_id: int):
        """Վերադարձնում է միայն այն հյուրերին, ովքեր դեռ սեղան չունեն (Չնստեցվածներ)"""
        return self.member_repo.get_unseated_by_wedding(wedding_id)

    def get_all_members_by_wedding(self, wedding_id: int):
        """Բերում է հարսանիքի բոլոր անդամներին սերվիսի միջոցով"""
        return self.member_repo.get_all_by_wedding(wedding_id)