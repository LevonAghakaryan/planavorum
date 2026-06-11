from sqlalchemy.orm import Session

from app.models.wedding import Wedding, _generate_token, _slugify
from app.schemas.wedding import WeddingCreate


class WeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── helpers ──────────────────────────────────────────────────────────────

    def _unique_slug(self, base: str) -> str:
        """Եթե slug-ը արդեն կա, ավելացնում է -2, -3 … մինչև ազատ գտնի։"""
        slug = base
        n = 2
        while self.db.query(Wedding).filter(Wedding.slug == slug).first():
            slug = f"{base}-{n}"
            n += 1
        return slug

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(self, wedding_data: WeddingCreate) -> Wedding:
        slug  = self._unique_slug(_slugify(wedding_data.title))
        token = _generate_token()

        db_wedding = Wedding(
            title=wedding_data.title,
            slug=slug,
            token=token,
        )
        self.db.add(db_wedding)
        self.db.commit()
        self.db.refresh(db_wedding)
        return db_wedding

    def get_by_id(self, wedding_id: int) -> Wedding | None:
        return self.db.query(Wedding).filter(Wedding.id == wedding_id).first()

    def get_by_slug(self, slug: str) -> Wedding | None:
        return self.db.query(Wedding).filter(Wedding.slug == slug).first()

    def get_by_token(self, token: str) -> Wedding | None:
        """Token-ով որոնում — security middleware-ի համար։"""
        return self.db.query(Wedding).filter(Wedding.token == token).first()