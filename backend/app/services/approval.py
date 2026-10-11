"""
Approval Service.

Handles human-in-the-loop approval requests for sensitive actions.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.approval import Approval, ApprovalStatus
from app.models.task import Task, TaskStatus
from app.models.agent_log import AgentLog, LogLevel


class ApprovalService:
    """Service to manage human approvals."""

    def create_request(
        self,
        db: Session,
        task: Task,
        action: str,
        details: Optional[str] = None,
    ) -> Approval:
        """Create a new approval request for a task."""
        approval = Approval(
            task_id=task.id,
            action=action,
            details=details,
            status=ApprovalStatus.PENDING,
        )
        db.add(approval)

        # Mark task as waiting approval
        task.status = TaskStatus.WAITING_APPROVAL

        # Log the request
        log = AgentLog(
            task_id=task.id,
            agent_type="approval",
            level=LogLevel.WARNING,
            message=f"Human approval requested: {action}",
            details=details,
        )
        db.add(log)
        db.commit()
        db.refresh(approval)

        return approval

    def list_pending(self, db: Session) -> List[Approval]:
        """List all pending approvals."""
        return (
            db.query(Approval)
            .filter(Approval.status == ApprovalStatus.PENDING)
            .order_by(Approval.requested_at.desc())
            .all()
        )

    def list_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Approval]:
        """List all approvals."""
        return (
            db.query(Approval)
            .order_by(Approval.requested_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, db: Session, approval_id: int) -> Optional[Approval]:
        """Get approval by ID."""
        return db.query(Approval).filter(Approval.id == approval_id).first()

    def respond(
        self,
        db: Session,
        approval: Approval,
        status: ApprovalStatus,
    ) -> Approval:
        """
        Approve or reject an approval request.

        Also updates the linked task status accordingly.
        """
        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(
                f"Approval already {approval.status.value}. Cannot respond again."
            )

        if status not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise ValueError("Status must be 'approved' or 'rejected'.")

        # Update approval
        approval.status = status
        approval.responded_at = datetime.now(timezone.utc)

        # Update task based on decision
        task = db.query(Task).filter(Task.id == approval.task_id).first()
        if task:
            if status == ApprovalStatus.APPROVED:
                task.status = TaskStatus.COMPLETED
                log_level = LogLevel.SUCCESS
                log_message = f"Approval GRANTED: {approval.action}"
            else:
                task.status = TaskStatus.FAILED
                task.error = f"Rejected by human: {approval.action}"
                log_level = LogLevel.ERROR
                log_message = f"Approval REJECTED: {approval.action}"

            log = AgentLog(
                task_id=task.id,
                agent_type="human",
                level=log_level,
                message=log_message,
            )
            db.add(log)

        db.commit()
        db.refresh(approval)

        return approval


# Singleton
approval_service = ApprovalService()