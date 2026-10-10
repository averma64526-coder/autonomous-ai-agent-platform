"""
Task API routes - execute tasks and list logs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.task import Task
from app.models.agent_log import AgentLog
from app.schemas.task import TaskRead, TaskExecuteResponse
from app.services.executor import executor_agent

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# --- LIST TASKS FOR A GOAL ---
@router.get("/by-goal/{goal_id}", response_model=List[TaskRead])
def list_tasks_for_goal(goal_id: int, db: Session = Depends(get_db)):
    """List all tasks for a given goal."""
    tasks = (
        db.query(Task)
        .filter(Task.goal_id == goal_id)
        .order_by(Task.order)
        .all()
    )
    return tasks


# --- GET ONE TASK ---
@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


# --- EXECUTE TASK (AI) ---
@router.post("/{task_id}/execute", response_model=TaskExecuteResponse)
def execute_task(task_id: int, db: Session = Depends(get_db)):
    """
    Execute a task using AI.
    The result is saved to the database and logged.
    """
    # 1. Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # 2. Check if already completed
    if task.status.value in ("completed", "running"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is already {task.status.value}",
        )

    # 3. Execute using AI
    try:
        result = executor_agent.execute(task=task, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}",
        )

    # 4. Reload task
    db.refresh(task)

    return TaskExecuteResponse(
        task_id=task.id,
        status=task.status,
        result=task.result,
        steps=result.get("steps", []),
        confidence=result.get("confidence", 0.0),
    )


# --- LIST LOGS FOR A TASK ---
@router.get("/{task_id}/logs")
def list_task_logs(task_id: int, db: Session = Depends(get_db)):
    """List all agent logs for a task."""
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.task_id == task_id)
        .order_by(AgentLog.created_at)
        .all()
    )
    return [
        {
            "id": log.id,
            "agent_type": log.agent_type,
            "level": log.level.value,
            "message": log.message,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]
