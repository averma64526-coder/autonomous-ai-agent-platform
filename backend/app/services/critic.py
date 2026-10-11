"""
Critic Agent.

Recovers failed tasks by proposing a fix and re-executing.
"""

import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.agent_log import AgentLog, LogLevel
from app.services.llm import llm_service
from app.prompts.task_prompts import (
    TASK_RECOVERY_SYSTEM_PROMPT,
    TASK_RECOVERY_USER_PROMPT,
)


class CriticAgent:
    """Agent that recovers failed tasks."""

    name = "critic"

    def _log(
        self,
        db: Session,
        task_id: int,
        level: LogLevel,
        message: str,
        details: str = None,
    ):
        """Write a log entry."""
        log = AgentLog(
            task_id=task_id,
            agent_type=self.name,
            level=level,
            message=message,
            details=details,
        )
        db.add(log)
        db.commit()

    def recover(
        self,
        task: Task,
        db: Session,
        issues: list = None,
    ) -> Dict[str, Any]:
        """
        Recover a failed task by generating a better result.

        Args:
            task: The task to recover.
            db: Database session.
            issues: List of issues from verifier (optional).

        Returns:
            dict with fix_strategy, steps, result, confidence
        """
        if not task.result and not task.error:
            raise ValueError("Task has no result or error to recover from.")

        self._log(
            db,
            task.id,
            LogLevel.INFO,
            f"Starting recovery of task: {task.title}",
        )

        try:
            issues_text = (
                "\n".join(f"- {i}" for i in issues)
                if issues
                else task.error or "No specific issues listed."
            )

            user_prompt = TASK_RECOVERY_USER_PROMPT.format(
                task_title=task.title,
                task_description=task.description or "(no description)",
                previous_result=task.result or "(no result)",
                issues=issues_text,
            )

            self._log(
                db,
                task.id,
                LogLevel.INFO,
                "Calling AI to generate recovery plan...",
            )

            response = llm_service.chat_json(
                system_prompt=TASK_RECOVERY_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,
            )

            fix_strategy = str(response.get("fix_strategy", ""))
            steps = response.get("steps", [])
            new_result = str(response.get("result", ""))
            confidence = float(response.get("confidence", 0.0))

            if not new_result:
                raise ValueError("AI did not return an improved result.")

            # Update task with improved result
            task.result = new_result
            task.status = TaskStatus.COMPLETED
            task.error = None  # Clear previous error
            db.commit()

            self._log(
                db,
                task.id,
                LogLevel.SUCCESS,
                f"Task recovered successfully (confidence: {confidence})",
                details=json.dumps(
                    {
                        "fix_strategy": fix_strategy,
                        "steps": steps,
                        "confidence": confidence,
                    },
                    indent=2,
                ),
            )

            return {
                "fix_strategy": fix_strategy,
                "steps": steps,
                "result": new_result,
                "confidence": confidence,
            }

        except Exception as e:
            self._log(
                db,
                task.id,
                LogLevel.ERROR,
                f"Recovery failed: {str(e)}",
            )
            raise


# Singleton
critic_agent = CriticAgent()