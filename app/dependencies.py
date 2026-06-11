"""
app/dependencies.py
"""

import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from core.database import get_db
from app.repositories.wedding   import WeddingRepository
from app.services.wedding       import WeddingService
from app.services.table         import TableService
from app.services.guest         import GuestService
from app.services.guest_members import GuestMemberService


# ── Token verification ────────────────────────────────────────────────────────

def verify_wedding_token(
    request: Request,
    x_wedding_token: str = Header(..., alias="X-Wedding-Token"),
    wid: Optional[int] = Query(None, alias="wedding_id"),  # query param-ի alias
    db: Session = Depends(get_db),
) -> int:
    """
    wedding_id-ն կարդում է.
      1. Path param-ից  — request.path_params (FastAPI-ն ինքը լրացնում է)
      2. Query param-ից — ?wedding_id=2
    Token-ը ստուգում է DB-ում timing-safe համեմատությամբ։
    """
    path_id     = request.path_params.get("wedding_id")
    resolved_id = int(path_id) if path_id is not None else wid

    if resolved_id is None:
        raise HTTPException(status_code=400, detail="wedding_id պարտադիր է")

    repo    = WeddingRepository(db)
    wedding = repo.get_by_id(resolved_id)

    if not wedding:
        raise HTTPException(status_code=404, detail="Wedding not found")

    if not secrets.compare_digest(wedding.token, x_wedding_token):
        raise HTTPException(status_code=403, detail="Invalid token")

    return resolved_id


# ── Service factories ─────────────────────────────────────────────────────────

def get_wedding_service(db: Session = Depends(get_db)) -> WeddingService:
    return WeddingService(db)

def get_table_service(db: Session = Depends(get_db)) -> TableService:
    return TableService(db)

def get_guest_service(db: Session = Depends(get_db)) -> GuestService:
    return GuestService(db)

def get_guest_member_service(db: Session = Depends(get_db)) -> GuestMemberService:
    return GuestMemberService(db)