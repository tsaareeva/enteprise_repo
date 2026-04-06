from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class CustomerCreateDto(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class CustomerDto(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WelcomeEmailMessage(BaseModel):
    customer_id: int
    email: str
    first_name: str
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }