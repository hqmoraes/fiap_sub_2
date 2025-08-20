from fastapi import APIRouter, HTTPException, Query
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.infrastructure.db import SessionLocal
from app.domain.models import Vehicle, Sale, VehicleStatus
from app.domain.schemas import VehicleCreate, VehicleUpdate, VehicleOut, SellRequest

router = APIRouter()

@router.post("/", response_model=VehicleOut, status_code=201)
def create_vehicle(payload: VehicleCreate):
    with SessionLocal() as db:
        v = Vehicle(
            brand=payload.brand,
            model=payload.model,
            year=payload.year,
            color=payload.color,
            price=payload.price,
        )
        db.add(v)
        db.commit()
        db.refresh(v)
        return _to_vehicle_out(v)

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: int, payload: VehicleUpdate):
    with SessionLocal() as db:
        v = db.get(Vehicle, vehicle_id)
        if not v:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        if v.status != VehicleStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Cannot edit a sold vehicle")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(v, field, value)
        db.add(v)
        db.commit()
        db.refresh(v)
        return _to_vehicle_out(v)

@router.get("/", response_model=List[VehicleOut])
def list_vehicles(
    status: VehicleStatus = Query(..., description="AVAILABLE or SOLD"),
    page: int = 1,
    size: int = 50,
):
    with SessionLocal() as db:
        offset = (page - 1) * size
        stmt = (
            select(Vehicle)
            .where(Vehicle.status == status)
            .order_by(Vehicle.price.asc())
            .offset(offset)
            .limit(size)
        )
        rows = db.execute(stmt).scalars().all()
        return [_to_vehicle_out(v) for v in rows]

@router.post("/{vehicle_id}/sell")
def sell_vehicle(vehicle_id: int, payload: SellRequest):
    with SessionLocal() as db:
        v = db.get(Vehicle, vehicle_id)
        if not v:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        if v.status != VehicleStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Vehicle already sold")
        v.status = VehicleStatus.SOLD
        sale = Sale(
            vehicle_id=v.id,
            buyer_cpf=payload.buyerCpf,
            sale_date=payload.saleDate,
            sale_price=payload.salePrice,
            payment_code=payload.paymentCode,
        )
        db.add_all([v, sale])
        db.commit()
        return {"saleId": sale.id, "vehicleId": v.id}

# helpers

def _to_vehicle_out(v: Vehicle) -> VehicleOut:
    return VehicleOut(
        id=v.id,
        brand=v.brand,
        model=v.model,
        year=v.year,
        color=v.color,
        price=v.price,
        status=v.status,
        createdAt=v.created_at,
        updatedAt=v.updated_at,
    )
