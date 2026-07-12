from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    due_date: str
    start_time: Optional[str] = None  # Format: HH:MM (contoh: 11:00)
    duration_minutes: Optional[int] = None  # Durasi dalam menit


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None