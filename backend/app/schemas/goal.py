"""
Pydantic schemas for Goal - request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.goal import GoalStatus


# ─── Base Schema (shared fields) ───
class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Goal title")
    description: Optional[str] = Field(None, description="Detailed description")


# ─── Create Schema (for POST) ───
class GoalCreate(GoalBase):
    """Schema for creating a new goal."""
    pass


# ─── Update Schema (for PUT/PATCH) ───
class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None


# ─── Read Schema (for GET) ───
class GoalRead(GoalBase):
    """Schema for reading a goal from database."""
    id: int
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── List Schema ───
class GoalListResponse(BaseModel):
    """Response for listing goals."""
    total: int
    goals: List[GoalRead]
