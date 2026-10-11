"""
Verifier Agent.

Checks whether a task's result is valid and complete.
"""

import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.agent_log import AgentLog, LogLevel
from app.services.llm import llm_service
from app.prompts.task_prompts import (
    TASK_VERIFICATION_SYSTEM_PROMPT,
    TASK_VERIFICATION_USER_PROMPT,
)


class VerifierAgent:
    """Agent that verifies task results."""

    name = "verifier"

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

    def verify(self, task: Task, db: Session) -> Dict[str, Any]:
        """
        Verify a completed task's result.

        Returns:
            dict with is_valid, score, issues, feedback
        """
        # Check task is completed
        if task.status != TaskStatus.COMPLETED:
            raise ValueError(
                f"Cannot verify task with status '{task.status.value}'. "
                "Task must be completed first."
            )

        if not task.result:
            raise ValueError("Task has no result to verify.")

        self._log(
            db,
            task.id,
            LogLevel.INFO,
            f"Starting verification of task: {task.title}",
        )

        try:
            user_prompt = TASK_VERIFICATION_USER_PROMPT.format(
                task_title=task.title,
                task_description=task.description or "(no description)",
                task_result=task.result,
            )

            self._log(
                db,
                task.id,
                LogLevel.INFO,
                "Calling AI to verify result...",
            )

            response = llm_service.chat_json(
                system_prompt=TASK_VERIFICATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.2,
            )

            is_valid = bool(response.get("is_valid", False))
            score = float(response.get("score", 0.0))
            issues = response.get("issues", [])
            feedback = str(response.get("feedback", ""))

            # If invalid, mark task as failed
            if not is_valid or score < 0.7:
                task.error = f"Verification failed: {feedback}"
                db.commit()

                self._log(
                    db,
                    task.id,
                    LogLevel.WARNING,
                    f"Verification FAILED (score: {score}): {feedback}",
                    details=json.dumps(
                        {"issues": issues, "score": score}, indent=2
                    ),
                )
            else:
                self._log(
                    db,
                    task.id,
                    LogLevel.SUCCESS,
                    f"Verification PASSED (score: {score})",
                    details=json.dumps({"score": score}, indent=2),
                )

            return {
                "is_valid": is_valid,
                "score": score,
                "issues": issues,
                "feedback": feedback,
            }

        except Exception as e:
            self._log(
                db,
                task.id,
                LogLevel.ERROR,
                f"Verification error: {str(e)}",
            )
            raise


# Singleton
verifier_agent = VerifierAgent()