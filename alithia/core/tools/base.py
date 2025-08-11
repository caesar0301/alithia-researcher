from __future__ import annotations

from pydantic import BaseModel

# Re-export LangChain BaseTool to ensure ecosystem compatibility


class ToolInput(BaseModel):
    """Base class for tool input models."""


class ToolOutput(BaseModel):
    """Base class for tool output models."""
