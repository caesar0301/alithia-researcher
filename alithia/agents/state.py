"""
Agent state management for the Alithia research agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.paper import ArxivPaper, EmailContent, ScoredPaper
from ..models.profile import ResearchProfile


@dataclass
class AgentState:
    """Centralized state for the research agent workflow."""

    # User Profile
    profile: Optional[ResearchProfile] = None

    # Discovery State
    discovered_papers: List[ArxivPaper] = field(default_factory=list)
    zotero_corpus: List[Dict[str, Any]] = field(default_factory=list)

    # Assessment State
    scored_papers: List[ScoredPaper] = field(default_factory=list)

    # Content State
    email_content: Optional[EmailContent] = None

    # System State
    current_step: str = "initializing"
    error_log: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    # Debug State
    debug_mode: bool = False

    def add_error(self, error: str) -> None:
        """Add an error to the error log."""
        self.error_log.append(f"{datetime.now().isoformat()}: {error}")

    def update_metric(self, key: str, value: float) -> None:
        """Update a performance metric."""
        self.performance_metrics[key] = value

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        return {
            "current_step": self.current_step,
            "papers_discovered": len(self.discovered_papers),
            "papers_scored": len(self.scored_papers),
            "errors": len(self.error_log),
            "metrics": self.performance_metrics,
        }
