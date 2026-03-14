from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.customer_service import CustomerService
from app.security import get_current_user, check_role
from app.schemas import CustomerCreate, CustomerUpdate, CustomerListResponse, CustomerResponse
from app.models import User
from math import ceil

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


def get_service(db: Session = Depends(get_db)):
    return CustomerService(db)


@router.get("/", response_model=CustomerListResponse)
def get_customers(
        page: int = Query(0, ge=0),
        size: int = Query(10, ge=1, le=100),
        sort: str = Query("id,asc"),
        firstName: str = None,
        lastName: str = None,
        email: str = None,
        service: CustomerService = Depends(get_service),
        current_user: User = Depends(check_role("ROLE_USER"))
):
    skip = page * size
    sort_by, order = sort.split(",") if "," in sort else ("id", "asc")

    filters = {"first_name": firstName, "last_name": lastName, "email": email}
    filters = {k: v for k, v in filters.items() if v is not None}

    items, total = service.get_all_customers(skip, size, filters, sort_by, order)

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": ceil(total / size) if size > 0 else 0
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
        customer_id: int,
        service: CustomerService = Depends(get_service),
        current_user: User = Depends(check_role("ROLE_USER"))
):
    customer = service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerResponse)
def create_customer(
        customer: CustomerCreate,
        service: CustomerService = Depends(get_service),
        current_user: User = Depends(check_role("ROLE_ADMIN"))
):
    return service.create_customer(customer.model_dump())


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
        customer_id: int,
        customer: CustomerUpdate,
        service: CustomerService = Depends(get_service),
        current_user: User = Depends(check_role("ROLE_ADMIN"))
):
    db_customer = service.update_customer(customer_id, customer.model_dump())
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.delete("/{customer_id}")
def delete_customer(
        customer_id: int,
        service: CustomerService = Depends(get_service),
        current_user: User = Depends(check_role("ROLE_ADMIN"))
):
    deleted = service.delete_customer(customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Deleted"}