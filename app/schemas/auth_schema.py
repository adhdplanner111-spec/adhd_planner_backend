from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str