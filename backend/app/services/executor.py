"""
Executor Agent.

Takes a task and executes it using LLM.
Produces a simulated result and logs the process.
"""

import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.agent_log import AgentLog, LogLevel
from app.services.llm import llm_service
from app.prompts.task_prompts import (
    TASK_EXECUTION_SYSTEM_PROMPT,
    TASK_EXECUTION_USER_PROMPT,
)


class ExecutorAgent:
    """Agent that executes tasks using AI."""

    name = "executor"

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

    def execute(self, task: Task, db: Session) -> Dict[str, Any]:
        """
        Execute a task using AI.

        Steps:
        1. Mark task as RUNNING
        2. Log start
        3. Call AI for execution plan
        4. Save result
        5. Mark task as COMPLETED
        6. Log completion

        Returns:
            dict with steps, result, confidence
        """
        # 1. Mark running
        task.status = TaskStatus.RUNNING
        db.commit()

        # 2. Log start
        self._log(
            db,
            task.id,
            LogLevel.INFO,
            f"Starting execution of task: {task.title}",
        )

        # 3. Call AI
        try:
            user_prompt = TASK_EXECUTION_USER_PROMPT.format(
                task_title=task.title,
                task_description=task.description or "(no description)",
            )

            self._log(
                db,
                task.id,
                LogLevel.INFO,
                "Calling AI to generate execution plan...",
            )

            response = llm_service.chat_json(
                system_prompt=TASK_EXECUTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,
            )

            steps = response.get("steps", [])
            result = response.get("result", "")
            confidence = response.get("confidence", 0.0)

            if not result:
                raise ValueError("AI did not return a result.")

            # 4. Save result
            task.result = result
            task.status = TaskStatus.COMPLETED
            db.commit()

            self._log(
                db,
                task.id,
                LogLevel.SUCCESS,
                f"Task completed successfully (confidence: {confidence})",
                details=json.dumps({"steps": steps, "confidence": confidence}),
            )

            return {
                "steps": steps,
                "result": result,
                "confidence": confidence,
            }

        except Exception as e:
            # Handle failure
            task.status = TaskStatus.FAILED
            task.error = str(e)
            db.commit()

            self._log(
                db,
                task.id,
                LogLevel.ERROR,
                f"Task execution failed: {str(e)}",
            )

            raise


# Singleton
executor_agent = ExecutorAgent()
