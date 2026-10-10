"""
Agent model - represents an AI agent in the multi-agent system.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class AgentType(str, enum.Enum):
    """Type of agent role."""
    PLANNER = "planner"
    EXECUTOR = "executor"
    VERIFIER = "verifier"
    CRITIC = "critic"


class AgentStatus(str, enum.Enum):
    """Status of an agent."""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class Agent(Base):
    """Agent - an AI agent that performs tasks."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False)
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus),
        default=AgentStatus.IDLE,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', type={self.type})>"
