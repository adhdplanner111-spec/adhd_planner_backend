from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminUpdateUserSchema(BaseModel):
    fullname: Optional[str] = None
    streak: Optional[int] = None
    productivity_score: Optional[int] = None

class CreateUserSchema(BaseModel):
    fullname: str
    email: EmailStr
    password: str