from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.schemas.table import TableCreate, TableResponse, TablePositionUpdate, TableBulkPositionUpdate
from app.services.table import TableService
from app.dependencies import get_table_service, verify_wedding_token

router = APIRouter(prefix="/api/v1/tables", tags=["Tables"])


@router.post("/", response_model=TableResponse)
def create_table(
    table_data: TableCreate,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    return service.create_table(table_data)


@router.get("/wedding/{wedding_id}", response_model=List[TableResponse])
def get_wedding_tables(
    wedding_id: int,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    return service.get_wedding_tables(wedding_id)

@router.put("/bulk-position")
def bulk_update_table_positions(
    wedding_id: int,
    payload: TableBulkPositionUpdate,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    updated = service.update_bulk_positions(wedding_id, payload)
    return {"updated": updated}

@router.get("/{table_id}/available-seats")
def get_available_seats(
    table_id: int,
    wedding_id: int,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    seats = service.get_table_available_seats(table_id)
    return {"table_id": table_id, "available_seats": seats}


@router.put("/{table_id}/capacity", response_model=TableResponse)
def update_table_capacity(
    table_id: int,
    capacity: int,
    wedding_id: int,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    return service.update_capacity(table_id, capacity)


@router.put("/{table_id}/position", response_model=TableResponse)
def update_table_position(
    table_id: int,
    wedding_id: int,
    pos: TablePositionUpdate,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    """Պահպանում է սեղանի x/y դիրքը կտավում։"""
    return service.update_position(table_id, pos.x_pos, pos.y_pos)


@router.delete("/{table_id}")
def delete_table(
    table_id: int,
    wedding_id: int,
    service: TableService = Depends(get_table_service),
    _: int = Depends(verify_wedding_token),
):
    if not service.delete_table(table_id):
        raise HTTPException(status_code=404, detail="Table not found")
    return {"message": "Table deleted successfully"}

