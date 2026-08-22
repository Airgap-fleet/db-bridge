"""Pydantic validation models for Mission Control Dashboard API."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class TaskCreate(BaseModel):
    """Validation model for task creation."""
    title: str = Field(..., min_length=3, description="Task title (min 3 chars)")
    description: str = Field(default="", description="Task description")
    assignee: Optional[str] = Field(default=None, description="Agent ID to assign")
    priority: int = Field(default=1, ge=0, le=3, description="Priority 0-3")
    skills: Optional[List[str]] = Field(default=None, description="Required skills")
    model_override: Optional[str] = Field(default=None, description="Model override")

    @field_validator("assignee", mode="before")
    @classmethod
    def validate_assignee(cls, v):
        """Convert empty string to None."""
        if v == "":
            return None
        return v


class TaskUpdate(BaseModel):
    """Validation model for task updates."""
    title: Optional[str] = Field(default=None, min_length=3)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    priority: Optional[int] = Field(default=None, ge=0, le=3)
    assignee: Optional[str] = Field(default=None)

    @field_validator("assignee", mode="before")
    @classmethod
    def validate_assignee(cls, v):
        """Convert empty string to None."""
        if v == "":
            return None
        return v

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v):
        """Validate status against allowed flow."""
        if v is not None:
            allowed = ["triage", "todo", "ready", "running", "blocked", "done"]
            if v not in allowed:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(allowed)}")
        return v


class TaskStatusUpdate(BaseModel):
    """Validation model for status-only update."""
    status: str = Field(..., description="New status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status against allowed flow."""
        allowed = ["triage", "todo", "ready", "running", "blocked", "done"]
        if v not in allowed:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(allowed)}")
        return v


class MessageCreate(BaseModel):
    """Validation model for message creation."""
    agent_id: str = Field(..., min_length=1, description="Agent ID (required)")
    content: str = Field(..., min_length=1, description="Message content (required)")
    task_ref: Optional[str] = Field(default=None, description="Optional task reference")
    channel: Optional[str] = Field(default="general", description="Channel name")
    agent_name: Optional[str] = Field(default=None, description="Agent display name")
    agent_color: Optional[str] = Field(default=None, description="Agent color hex")


class AgentCreate(BaseModel):
    """Validation model for agent creation."""
    id: str = Field(..., min_length=1, description="Agent ID (required)")
    name: str = Field(..., min_length=1, description="Agent name (required)")
    role: str = Field(..., min_length=1, description="Agent role (required)")
    color: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$", description="Hex color (e.g., #ff6b35)")
    profile_name: Optional[str] = Field(default=None, description="Hermes profile name")


def format_validation_error(e: Exception) -> dict:
    """Convert Pydantic ValidationError to standard error format."""
    if hasattr(e, "errors"):
        errors = {}
        for err in e.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            msg = err["msg"]
            errors[field] = msg
        return {"detail": errors}
    return {"detail": {"message": str(e)}}