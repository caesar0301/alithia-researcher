"""
Main research agent implementation using LangGraph.
"""

import logging
from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

from ..models.profile import ResearchProfile
from .nodes import (
    communication_node,
    content_generation_node,
    data_collection_node,
    profile_analysis_node,
    relevance_assessment_node,
)
from .state import AgentState

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    LangGraph-based research agent that replicates zotero-arxiv-daily functionality.
    """

    def __init__(self):
        """Initialize the research agent."""
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> CompiledGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("profile_analysis", profile_analysis_node)
        workflow.add_node("data_collection", data_collection_node)
        workflow.add_node("relevance_assessment", relevance_assessment_node)
        workflow.add_node("content_generation", content_generation_node)
        workflow.add_node("communication", communication_node)

        # Define edges (linear workflow)
        workflow.add_edge("profile_analysis", "data_collection")
        workflow.add_edge("data_collection", "relevance_assessment")
        workflow.add_edge("relevance_assessment", "content_generation")
        workflow.add_edge("content_generation", "communication")

        # Set entry and exit points
        workflow.set_entry_point("profile_analysis")
        workflow.set_finish_point("communication")

        return workflow.compile()

    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the research agent with given configuration.

        Args:
            config: Configuration dictionary with all necessary parameters

        Returns:
            Final state dictionary with results
        """
        logger.info("Starting research agent workflow...")

        # Create initial state
        profile = ResearchProfile.from_config(config)
        initial_state = AgentState(profile=profile, debug_mode=config.get("debug", False))

        try:
            # Run workflow
            final_state = self.workflow.invoke(initial_state)

            # Log summary
            summary = final_state.get_summary()
            logger.info(f"Workflow completed: {summary}")

            return {
                "success": True,
                "summary": summary,
                "papers_sent": len(final_state.scored_papers),
                "errors": final_state.error_log,
            }

        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {"success": False, "error": str(e), "errors": initial_state.error_log}

    def run_with_profile(self, profile: ResearchProfile, debug: bool = False) -> Dict[str, Any]:
        """
        Run the research agent with a pre-configured profile.

        Args:
            profile: ResearchProfile instance
            debug: Enable debug mode

        Returns:
            Final state dictionary with results
        """
        config = {
            "zotero_id": profile.zotero_id,
            "zotero_key": profile.zotero_key,
            "zotero_ignore": "\n".join(profile.ignore_patterns),
            "send_empty": profile.send_empty,
            "max_paper_num": profile.max_papers,
            "arxiv_query": profile.arxiv_query,
            "smtp_server": profile.smtp_server,
            "smtp_port": profile.smtp_port,
            "sender": profile.sender_email,
            "receiver": profile.receiver_email,
            "sender_password": profile.sender_password,
            "use_llm_api": profile.use_llm_api,
            "openai_api_key": profile.openai_api_key,
            "openai_api_base": profile.openai_api_base,
            "model_name": profile.model_name,
            "language": profile.language,
            "debug": debug,
        }

        return self.run(config)

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow structure.

        Returns:
            Dictionary with workflow information
        """
        return {
            "name": "Alithia Research Agent",
            "description": "LangGraph-based agent for daily ArXiv paper recommendations",
            "nodes": [
                "profile_analysis",
                "data_collection",
                "relevance_assessment",
                "content_generation",
                "communication",
            ],
            "entry_point": "profile_analysis",
            "exit_point": "communication",
        }
