"""Request and response bodies. These also produce the OpenAPI schema."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

WorkOrderStatus = Literal['new', 'in-progress', 'complete']
WorkOrderPriority = Literal['low', 'normal', 'high']


class WorkOrderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=400)
    reference: str = Field(default="", max_length=200)
    status: WorkOrderStatus = 'new'
    priority: WorkOrderPriority = 'normal'


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=400)
    reference: Optional[str] = Field(default=None, max_length=200)
    status: Optional[WorkOrderStatus] = None
    priority: Optional[WorkOrderPriority] = None


class WorkOrder(WorkOrderCreate):
    id: int
