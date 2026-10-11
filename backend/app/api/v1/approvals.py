"""
Approval API routes - human-in-the-loop approval management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.approval import Approval, ApprovalStatus
from app.schemas.approval import (
    ApprovalCreate,
    ApprovalRespond,
    ApprovalRead,
    ApprovalListResponse,
)
from app.services.approval import approval_service

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


# --- CREATE APPROVAL REQUEST ---
@router.post("", response_model=ApprovalRead, status_code=status.HTTP_201_CREATED)
def create_approval(payload: ApprovalCreate, db: Session = Depends(get_db)):
    """Create a new approval request."""
    from app.models.task import Task

    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {payload.task_id} not found",
        )

    try:
        approval = approval_service.create_request(
            db=db,
            task=task,
            action=payload.action,
            details=payload.details,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create approval: {str(e)}",
        )

    return approval


# --- LIST ALL APPROVALS ---
@router.get("", response_model=ApprovalListResponse)
def list_approvals(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
):
    """List all approvals, optionally filtered by status."""
    query = db.query(Approval)

    if status_filter:
        try:
            approval_status = ApprovalStatus(status_filter)
            query = query.filter(Approval.status == approval_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )

    total = query.count()
    approvals = (
        query.order_by(Approval.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ApprovalListResponse(total=total, approvals=approvals)


# --- LIST PENDING APPROVALS ---
@router.get("/pending", response_model=List[ApprovalRead])
def list_pending_approvals(db: Session = Depends(get_db)):
    """List all pending approvals."""
    return approval_service.list_pending(db)


# --- GET ONE APPROVAL ---
@router.get("/{approval_id}", response_model=ApprovalRead)
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """Get a single approval by ID."""
    approval = approval_service.get(db, approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval with id {approval_id} not found",
        )
    return approval


# --- RESPOND TO APPROVAL (APPROVE / REJECT) ---
@router.post("/{approval_id}/respond", response_model=ApprovalRead)
def respond_to_approval(
    approval_id: int,
    payload: ApprovalRespond,
    db: Session = Depends(get_db),
):
    """Approve or reject an approval request."""
    approval = approval_service.get(db, approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval with id {approval_id} not found",
        )

    if payload.status not in (
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'.",
        )

    try:
        updated = approval_service.respond(
            db=db,
            approval=approval,
            status=payload.status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to respond: {str(e)}",
        )

    return updated