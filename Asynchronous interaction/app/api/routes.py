from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import CustomerCreateDto, CustomerDto
from app.services.customer_service import CustomerService
from typing import List

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@router.post("", response_model=CustomerDto, status_code=201)
async def create_customer(dto: CustomerCreateDto, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    try:
        return await service.create_customer(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{customer_id}", response_model=CustomerDto)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    try:
        return await service.get_customer_by_id(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[CustomerDto])
async def get_all_customers(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = CustomerService(db)
    return await service.get_all_customers(skip, limit)

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    try:
        await service.delete_customer(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))