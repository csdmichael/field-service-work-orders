"""Request and response bodies. These also produce the OpenAPI schema."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["new", "in-progress", "complete"]
Priority = Literal["low", "normal", "high"]


class WorkItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=400)
    location: str = Field(default="", max_length=200)
    status: Status = "new"
    priority: Priority = "normal"


class WorkItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=400)
    location: Optional[str] = Field(default=None, max_length=200)
    status: Optional[Status] = None
    priority: Optional[Priority] = None


class WorkItem(WorkItemCreate):
    id: int
