from sqlalchemy.orm import Session
from app.models import Customer

def get_all(db: Session, skip: int, limit: int, filters, sort_by: str, order: str):
    if isinstance(filters, tuple):
        filters = dict(filters)

    query = db.query(Customer)

    if filters.get('first_name'):
        query = query.filter(Customer.first_name.ilike(f"%{filters['first_name']}%"))
    if filters.get('last_name'):
        query = query.filter(Customer.last_name.ilike(f"%{filters['last_name']}%"))
    if filters.get('email'):
        query = query.filter(Customer.email.ilike(f"%{filters['email']}%"))

    total = query.count()

    order_col = getattr(Customer, sort_by, Customer.id)
    if order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    items = query.offset(skip).limit(limit).all()
    return items, total

def get_by_id(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def create(db: Session, customer: Customer):
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def update(db: Session, customer_id: int, data: dict):
    db_customer = get_by_id(db, customer_id)
    if db_customer:
        for key, value in data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete(db: Session, customer_id: int):
    db_customer = get_by_id(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer