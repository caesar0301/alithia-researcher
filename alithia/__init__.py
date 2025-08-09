"""
Alithia Research Agent

A LangGraph-based agent system that replicates zotero-arxiv-daily functionality
using an agentic architecture with cogents.common.llm integration.
"""

from .agents.research_agent import ResearchAgent
from .models.paper import ArxivPaper
from .models.profile import ResearchProfile

__all__ = ["ResearchAgent", "ArxivPaper", "ResearchProfile"]
