from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ToolInput(BaseModel):
    """Base class for tool input models."""


class ToolOutput(BaseModel):
    """Base class for tool output models."""


class Tool(ABC):
    """Abstract base class for tools with a simple execute interface."""

    name: str
    description: str

    def __init__(self, name: Optional[str] = None, description: str = "") -> None:
        self.name = name or self.__class__.__name__
        self.description = description

    @abstractmethod
    def execute(self, inputs: ToolInput, **kwargs: Any) -> ToolOutput:
        """Run the tool and return structured output."""
        raise NotImplementedError

    # Helper to allow dict input in integration contexts
    def __call__(self, inputs: ToolInput | Dict[str, Any], **kwargs: Any) -> ToolOutput:
        if isinstance(inputs, dict):
            # Attempt to coerce dict into the tool's input model via type hints
            model_cls = getattr(self, "InputModel", None)
            if model_cls is None:
                raise TypeError("Tool is missing InputModel type for dict invocation.")
            inputs = model_cls(**inputs)
        return self.execute(inputs, **kwargs)