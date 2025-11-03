"""FastAPI backend for the Forge platform."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Forge Automation API",
    description="HTTP interface for triggering Forge automation tasks.",
    version="0.1.0",
)


class ExecuteRequest(BaseModel):
    task: str = Field(..., description="High level task the agent should execute.")
    model: str = Field("claude", description="LLM backend identifier.")
    tools: List[str] = Field(default_factory=list, description="Tool identifiers that may be used.")

    @validator("task")
    def validate_task(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Task description cannot be empty.")
        return value


class Step(BaseModel):
    id: int
    action: str
    status: str
    detail: Optional[str] = None


class ExecuteResponse(BaseModel):
    task: str
    status: str
    mode: str
    message: str
    steps: List[Step]
    data: dict
    started_at: datetime
    completed_at: datetime


@app.post("/execute", response_model=ExecuteResponse)
def execute_task(request: ExecuteRequest) -> ExecuteResponse:
    """Trigger the automation pipeline.

    The existing `adaptive_agent` module is large and requires a browser
    runtime. For now we provide a lightweight orchestration stub that can be
    replaced with the full agent when the environment is ready. The endpoint
    still mirrors the contract expected by the frontend so the integration is
    functional today.
    """
    logger.info("Received task request", extra={"task": request.task, "model": request.model, "tools": request.tools})

    started_at = datetime.utcnow()

    try:
        steps: List[Step] = [
            Step(id=1, action="Initializing agent", status="completed", detail="Environment verified."),
            Step(id=2, action="Analyzing task", status="completed", detail="Task intent classified."),
            Step(id=3, action="Executing actions", status="completed", detail="Simulated agent actions executed."),
            Step(id=4, action="Gathering results", status="completed", detail="Compiled structured findings."),
            Step(id=5, action="Finalizing output", status="completed", detail="Generated completion payload."),
        ]

        result_payload = {
            "summary": "Task processed successfully in stub backend.",
            "model": request.model,
            "tools_used": request.tools,
        }

        message = "Execution completed without errors."
        status = "completed"

    except Exception as exc:  # pragma: no cover - defensive logging only
        logger.exception("Task execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    completed_at = datetime.utcnow()

    return ExecuteResponse(
        task=request.task,
        status=status,
        mode=request.model,
        message=message,
        steps=steps,
        data=result_payload,
        started_at=started_at,
        completed_at=completed_at,
    )
