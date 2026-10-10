"""
Goal API routes - CRUD operations + AI decomposition.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.goal import Goal
from app.models.task import Task
from app.schemas.goal import (
    GoalCreate,
    GoalRead,
    GoalUpdate,
    GoalListResponse,
)
from app.schemas.task import TaskRead, DecomposeResponse
from app.services.decomposer import goal_decomposer

router = APIRouter(prefix="/api/v1/goals", tags=["goals"])


# --- CREATE ---
@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal."""
    goal = Goal(title=payload.title, description=payload.description)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


# --- LIST ---
@router.get("", response_model=GoalListResponse)
def list_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all goals with pagination."""
    total = db.query(Goal).count()
    goals = db.query(Goal).offset(skip).limit(limit).all()
    return GoalListResponse(total=total, goals=goals)


# --- GET ONE ---
@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """Get a single goal by ID."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )
    return goal


# --- UPDATE ---
@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db)):
    """Update a goal (partial update)."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


# --- DELETE ---
@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """Delete a goal by ID."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )
    db.delete(goal)
    db.commit()
    return None


# --- DECOMPOSE (AI) ---
@router.post("/{goal_id}/decompose", response_model=DecomposeResponse)
def decompose_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    Use AI to break a goal into actionable tasks.
    Tasks are automatically saved to the database.
    """
    # 1. Get the goal
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )

    # 2. Check if tasks already exist (avoid duplicates)
    existing = db.query(Task).filter(Task.goal_id == goal_id).count()
    if existing > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Goal {goal_id} already has {existing} tasks. Delete them first to re-decompose.",
        )

    # 3. Call AI
    try:
        ai_tasks = goal_decomposer.decompose(
            goal_title=goal.title,
            goal_description=goal.description or "",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI decomposition failed: {str(e)}",
        )

    # 4. Save tasks to database
    saved_tasks = []
    for t in ai_tasks:
        task = Task(
            goal_id=goal_id,
            title=t["title"],
            description=t["description"],
            order=t["order"],
        )
        db.add(task)
        saved_tasks.append(task)

    db.commit()
    for task in saved_tasks:
        db.refresh(task)

    return DecomposeResponse(
        goal_id=goal_id,
        tasks_created=len(saved_tasks),
        tasks=saved_tasks,
    )
