"""
Pydantic schemas for Approval - request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.approval import ApprovalStatus


class ApprovalBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=255)
    details: Optional[str] = None


class ApprovalCreate(ApprovalBase):
    """Schema for creating an approval request."""
    task_id: int


class ApprovalRespond(BaseModel):
    """Schema for approving/rejecting an approval."""
    status: ApprovalStatus  # approved or rejected


class ApprovalRead(ApprovalBase):
    """Schema for reading an approval."""
    id: int
    task_id: int
    status: ApprovalStatus
    requested_at: datetime
    responded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApprovalListResponse(BaseModel):
    total: int
    approvals: List[ApprovalRead]