from pydantic import BaseModel, EmailStr


class RegisterOTPRequest(BaseModel):
    fullname: str
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResendOTPRequest(BaseModel):
    email: EmailStr