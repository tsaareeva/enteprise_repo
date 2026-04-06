from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Customer
from app.schemas import CustomerCreateDto, CustomerDto
from app.producer import send_welcome_email
import time

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_customer(self, dto: CustomerCreateDto) -> CustomerDto:
        print("Создание нового клиента")
        print(f"Email: {dto.email}")
        print(f"Name: {dto.first_name} {dto.last_name}")

        start_time = time.time()

        result = await self.db.execute(
            select(Customer).where(Customer.email == dto.email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Клиент с таким email уже существует: {dto.email}")

        customer = Customer(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)

        print(f"Клиент сохранен в БД с ID: {customer.id}")

        await send_welcome_email(
            customer_id=customer.id,
            email=customer.email,
            first_name=customer.first_name
        )

        end_time = time.time()
        print(f"Время обработки запроса: {(end_time - start_time) * 1000:.0f} мс")
        print("Клиент создан")

        return CustomerDto(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            created_at=customer.created_at
        )

    async def get_customer_by_id(self, customer_id: int) -> CustomerDto:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()

        if not customer:
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        return CustomerDto(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            created_at=customer.created_at
        )

    async def get_all_customers(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(
            select(Customer).offset(skip).limit(limit)
        )
        customers = result.scalars().all()

        return [
            CustomerDto(
                id=c.id,
                first_name=c.first_name,
                last_name=c.last_name,
                email=c.email,
                created_at=c.created_at
            )
            for c in customers
        ]

    async def delete_customer(self, customer_id: int):
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()

        if not customer:
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        await self.db.delete(customer)
        await self.db.commit()
        print(f"Клиент {customer_id} удален")