from pydantic import BaseModel
from typing import Optional


class AdminUpdateUserSchema(BaseModel):
    fullname: Optional[str] = None
    streak: Optional[int] = None
    productivity_score: Optional[int] = None