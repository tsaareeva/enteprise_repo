from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse
)
from app.services.customer_service import CustomerService
from app.repositories.customer_repository import CustomerRepository
from app.database.session import get_db

router = APIRouter()


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    customer_repository = CustomerRepository(db)
    return CustomerService(customer_repository)

@router.get("/", response_model=CustomerListResponse)
def read_customers(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, ge=1, le=100, description="Количество записей на странице"),
        first_name: Optional[str] = Query(None, description="Фильтр по имени"),
        last_name: Optional[str] = Query(None, description="Фильтр по фамилии"),
        email: Optional[str] = Query(None, description="Фильтр по email"),
        service: CustomerService = Depends(get_customer_service)
):
    filters = {}
    if first_name:
        filters['first_name'] = first_name
    if last_name:
        filters['last_name'] = last_name
    if email:
        filters['email'] = email

    result = service.get_customers(page=page, per_page=per_page, filters=filters)

    return {
        "customers": result["customers"],
        "total": result["total"],
        "page": result["page"],
        "limit": result["per_page"]
    }


@router.get("/search", response_model=List[CustomerResponse])
def search_customers(
        query: str = Query(..., min_length=2, description="Поисковый запрос"),
        limit: int = Query(50, ge=1, le=100, description="Лимит результатов"),
        service: CustomerService = Depends(get_customer_service)
):
    customers = service.search_customers(query, limit=limit)
    return customers


@router.get("/stats")
def get_stats(service: CustomerService = Depends(get_customer_service)):
    return service.get_customer_stats()

@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
        customer_id: int,
        service: CustomerService = Depends(get_customer_service)
):
    customer = service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
        customer: CustomerCreate,
        service: CustomerService = Depends(get_customer_service)
):
    try:
        created_customer = service.create_customer(customer)
        if not created_customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать клиента"
            )
        return created_customer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
        customer_id: int,
        customer: CustomerUpdate,
        service: CustomerService = Depends(get_customer_service)
):
    try:
        updated_customer = service.update_customer(customer_id, customer)
        if not updated_customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить клиента"
            )
        return updated_customer
    except ValueError as e:
        if "не найден" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
        customer_id: int,
        service: CustomerService = Depends(get_customer_service)
):
    try:
        success = service.delete_customer(customer_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить клиента"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )