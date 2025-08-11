from __future__ import annotations

from pydantic import BaseModel

# Re-export LangChain BaseTool to ensure ecosystem compatibility
from langchain_core.tools import BaseTool as BaseTool


class ToolInput(BaseModel):
    """Base class for tool input models."""


class ToolOutput(BaseModel):
    """Base class for tool output models."""