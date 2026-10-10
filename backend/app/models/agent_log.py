"""
AgentLog model - tracks what each agent is doing.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class LogLevel(str, enum.Enum):
    """Level of the log entry."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class AgentLog(Base):
    """Log entry - records agent actions."""

    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[LogLevel] = mapped_column(
        SQLEnum(LogLevel),
        default=LogLevel.INFO,
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    task = relationship("Task", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AgentLog(id={self.id}, agent={self.agent_type}, level={self.level})>"
