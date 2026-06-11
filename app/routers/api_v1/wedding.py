from fastapi import APIRouter, Depends, HTTPException

from app.schemas.wedding import WeddingCreate, WeddingResponse
from app.services.wedding import WeddingService
from app.dependencies import get_wedding_service, verify_wedding_token

router = APIRouter(prefix="/api/v1/weddings", tags=["Weddings"])


@router.post("/", response_model=WeddingResponse)
def create_wedding(
    wedding_data: WeddingCreate,
    service: WeddingService = Depends(get_wedding_service),
):
    """Ստեղծում է հարսանիք, վերադարձնում slug + token (client-ը պահում է)."""
    return service.create_wedding(wedding_data)


@router.get("/{wedding_id}", response_model=WeddingResponse)
def get_wedding(
    wedding_id: int,
    service: WeddingService = Depends(get_wedding_service),
    _: int = Depends(verify_wedding_token),          # ← token check
):
    wedding = service.get_wedding(wedding_id)
    if not wedding:
        raise HTTPException(status_code=404, detail="Wedding not found")
    return wedding