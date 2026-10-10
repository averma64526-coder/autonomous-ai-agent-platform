"""
Goal API routes - CRUD operations for goals.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.goal import Goal
from app.schemas.goal import (
    GoalCreate,
    GoalRead,
    GoalUpdate,
    GoalListResponse,
)

router = APIRouter(prefix="/api/v1/goals", tags=["goals"])


# ─── CREATE ───
@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal."""
    goal = Goal(
        title=payload.title,
        description=payload.description,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


# ─── LIST ───
@router.get("", response_model=GoalListResponse)
def list_goals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all goals with pagination."""
    total = db.query(Goal).count()
    goals = db.query(Goal).offset(skip).limit(limit).all()
    return GoalListResponse(total=total, goals=goals)


# ─── GET ONE ───
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


# ─── UPDATE ───
@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
):
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


# ─── DELETE ───
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
