from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.repositories.customer_repository import CustomerRepository
from app.domain.models import Customer


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.customer_repository.get(customer_id)

    def get_customers(
            self,
            page: int = 1,
            per_page: int = 10,
            filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return self.customer_repository.get_customers_with_pagination(
            page=page,
            per_page=per_page,
            filters=filters
        )

    def search_customers(self, query: str, limit: int = 50) -> List[Customer]:
        return self.customer_repository.search(query, limit=limit)

    def create_customer(self, customer_data: CustomerCreate) -> Optional[Customer]:
        if self.customer_repository.exists(email=customer_data.email):
            raise ValueError(f"Клиент с email {customer_data.email} уже существует")

        customer_dict = customer_data.model_dump()
        return self.customer_repository.create(customer_dict)

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        db_customer = self.customer_repository.get(customer_id)
        if not db_customer:
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        update_dict = customer_data.model_dump(exclude_unset=True)

        if 'email' in update_dict and update_dict['email'] != db_customer.email:
            if self.customer_repository.exists(email=update_dict['email']):
                raise ValueError(f"Клиент с email {update_dict['email']} уже существует")

        return self.customer_repository.update(db_customer, update_dict)

    def delete_customer(self, customer_id: int) -> bool:
        if not self.customer_repository.get(customer_id):
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        return self.customer_repository.delete(customer_id)

    def get_customer_stats(self) -> Dict[str, Any]:
        total = self.customer_repository.count()

        return {
            "total_customers": total,
            "stats": {
                "message": "Дополнительная статистика может быть добавлена здесь"
            }
        }