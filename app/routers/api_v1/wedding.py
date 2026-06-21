from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.schemas.wedding import WeddingCreate, WeddingUpdate, WeddingResponse
from app.services.wedding import WeddingService
from app.dependencies import get_wedding_service, verify_wedding_token, verify_admin

router = APIRouter(prefix="/api/v1/weddings", tags=["Weddings"])


# ── Admin endpoints (HTTP Basic Auth) ────────────────────────────────────────

@router.get("/list", response_model=List[WeddingResponse])
def list_all_weddings(
    service: WeddingService = Depends(get_wedding_service),
    _: bool = Depends(verify_admin),
):
    """Բոլոր հարսանիքները — admin dashboard-ի համար։"""
    return service.get_all_weddings()


@router.post("/", response_model=WeddingResponse)
def create_wedding(
    wedding_data: WeddingCreate,
    service: WeddingService = Depends(get_wedding_service),
    _: bool = Depends(verify_admin),
):
    """Ստեղծում է հարսանիք, վերադարձնում slug + token։"""
    return service.create_wedding(wedding_data)


@router.put("/{wedding_id}", response_model=WeddingResponse)
def update_wedding_title(
    wedding_id: int,
    body: WeddingUpdate,
    service: WeddingService = Depends(get_wedding_service),
    _: bool = Depends(verify_admin),
):
    """Փոխում է հարսանիքի անվանումը (admin only)։"""
    updated = service.update_title(wedding_id, body.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Wedding not found")
    return updated


@router.delete("/{wedding_id}")
def delete_wedding(
    wedding_id: int,
    service: WeddingService = Depends(get_wedding_service),
    _: bool = Depends(verify_admin),
):
    """Ջնջում է հարսանիքը cascade-ով (բոլոր սեղ. + հյ.)։"""
    if not service.delete_wedding(wedding_id):
        raise HTTPException(status_code=404, detail="Wedding not found")
    return {"message": "Deleted"}


# ── Token-protected endpoint (existing) ──────────────────────────────────────

@router.get("/{wedding_id}", response_model=WeddingResponse)
def get_wedding(
    wedding_id: int,
    service: WeddingService = Depends(get_wedding_service),
    _: int = Depends(verify_wedding_token),
):
    wedding = service.get_wedding(wedding_id)
    if not wedding:
        raise HTTPException(status_code=404, detail="Wedding not found")
    return wedding