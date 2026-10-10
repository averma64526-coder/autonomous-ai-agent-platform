"""
Pydantic schemas for Task - request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    order: int = 0


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskRead(TaskBase):
    """Schema for reading a task."""
    id: int
    goal_id: int
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    total: int
    tasks: List[TaskRead]


class DecomposeResponse(BaseModel):
    """Response for goal decomposition."""
    goal_id: int
    tasks_created: int
    tasks: List[TaskRead]
class TaskExecuteResponse(BaseModel):
    """Response for task execution."""
    task_id: int
    status: TaskStatus
    result: Optional[str] = None
    steps: List[str] = []
    confidence: float = 0.0