from pydantic import BaseModel

class AdminLoginSchema(BaseModel):
    username: str
    password: str