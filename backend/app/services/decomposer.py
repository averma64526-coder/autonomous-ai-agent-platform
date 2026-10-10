"""
Goal Decomposer Service.

Uses LLM to break a high-level goal into actionable tasks.
"""

from typing import List, Dict, Any

from app.services.llm import llm_service
from app.prompts.goal_prompts import (
    GOAL_DECOMPOSITION_SYSTEM_PROMPT,
    GOAL_DECOMPOSITION_USER_PROMPT,
)


class GoalDecomposer:
    """Service to decompose a goal into tasks using AI."""

    def decompose(self, goal_title: str, goal_description: str = "") -> List[Dict[str, Any]]:
        """
        Break a goal into tasks using the LLM.

        Args:
            goal_title: The goal's title.
            goal_description: Optional detailed description.

        Returns:
            List of task dicts: [{"title": ..., "description": ..., "order": ...}, ...]

        Raises:
            ValueError: If LLM returns invalid data.
        """
        # Build the prompts
        user_prompt = GOAL_DECOMPOSITION_USER_PROMPT.format(
            goal_title=goal_title,
            goal_description=goal_description or "(no description provided)",
        )

        # Call the LLM
        response = llm_service.chat_json(
            system_prompt=GOAL_DECOMPOSITION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
        )

        # Extract tasks
        tasks = response.get("tasks", [])

        if not isinstance(tasks, list) or len(tasks) == 0:
            raise ValueError("LLM did not return any tasks.")

        # Normalize: ensure every task has title, description, order
        normalized = []
        for i, task in enumerate(tasks, start=1):
            normalized.append({
                "title": str(task.get("title", f"Task {i}")).strip(),
                "description": str(task.get("description", "")).strip(),
                "order": int(task.get("order", i)),
            })

        # Sort by order
        normalized.sort(key=lambda t: t["order"])

        return normalized


# Singleton
goal_decomposer = GoalDecomposer()
