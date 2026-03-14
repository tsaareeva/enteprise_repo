from sqlalchemy.orm import Session
from app.repositories import customer_repo
from app.cache_manager import get_customer_cache, get_all_customers_cache, clear_customer_cache
from cachetools import cached
from app.models import Customer

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    @cached(cache=get_customer_cache())
    def get_customer_by_id(self, customer_id: int):
        return customer_repo.get_by_id(self.db, customer_id)

    @cached(cache=get_all_customers_cache())
    def get_all_customers(self, skip: int, limit: int, filters: dict, sort_by: str, order: str):
        key_filters = tuple(sorted((k, v) for k, v in filters.items() if v is not None))
        return customer_repo.get_all(self.db, skip, limit, key_filters, sort_by, order)

    def create_customer(self, data: dict):
        clear_customer_cache()
        db_customer = Customer(**data)
        return customer_repo.create(self.db, db_customer)

    def update_customer(self, customer_id: int, data: dict):
        clear_customer_cache()
        return customer_repo.update(self.db, customer_id, data)

    def delete_customer(self, customer_id: int):
        clear_customer_cache()
        return customer_repo.delete(self.db, customer_id)