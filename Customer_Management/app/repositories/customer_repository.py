from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.domain.models import Customer
from app.repositories.base import BaseRepository

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def get_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def search(
            self,
            query: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Customer]:
        search_query = f"%{query}%"
        return self.db.query(Customer).filter(
            or_(
                Customer.first_name.ilike(search_query),
                Customer.last_name.ilike(search_query),
                Customer.email.ilike(search_query)
            )
        ).offset(skip).limit(limit).all()

    def get_customers_with_pagination(
            self,
            page: int = 1,
            per_page: int = 10,
            filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        skip = (page - 1) * per_page
        customers = self.get_all(skip=skip, limit=per_page, filters=filters, order_by="created_at")
        total = self.count(filters=filters)

        return {
            "customers": customers,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }