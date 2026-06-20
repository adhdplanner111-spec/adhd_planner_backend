from pydantic import BaseModel, Field
from typing import Optional, Literal


class FocusPlanCreate(BaseModel):
    total_focus_minutes: int = Field( ..., ge=30, description="Total target fokus dalam menit" )
    focus_duration: int = Field( default=30, ge=15, description="Durasi fokus per siklus" )
    break_duration: int = Field( default=5, ge=1, description="Durasi istirahat per siklus" )
    task_id: Optional[str] = None

class FocusSessionCreate(BaseModel):
    cycle: int = Field(..., ge=1)
    type: Literal["focus", "break"]
    duration: int = Field(..., ge=1)