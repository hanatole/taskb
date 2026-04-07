from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class TaskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    due_date: date = Field(
        ..., description="Due date in YYYY-MM-DD format", alias="dueDate"
    )
    priority: Literal["LOW", "MEDIUM", "HIGH"]


class TaskResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: int
    title: str
    description: str | None
    due_date: date = Field(..., alias="dueDate")
    priority: str
    status: str
