from datetime import date
from typing import Optional

from sqlmodel import Field

from settings import SQLModel


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    due_date: date
    priority: str
    status: str
