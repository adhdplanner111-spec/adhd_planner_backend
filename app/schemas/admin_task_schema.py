from pydantic import BaseModel
from typing import Optional


class AdminUpdateTaskSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None