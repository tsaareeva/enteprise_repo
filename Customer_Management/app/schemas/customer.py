from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from datetime import datetime
from typing import Optional
import re


class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя клиента")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия клиента")
    email: EmailStr = Field(..., description="Email клиента")

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Имя не может быть пустым")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', v):
            raise ValueError("Имя может содержать только буквы и дефисы")
        return v.strip()


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    customers: list[CustomerResponse]
    total: int
    page: int
    limit: int