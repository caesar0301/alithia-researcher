"""
AlithiaVigil: Proactive Topic Monitoring Agent
"""

import logging
from typing import Any, Dict

from langgraph.graph import StateGraph

from alithia.core.state import AgentState
from .nodes import filter_results_node, scan_sources_node, send_alert_node

logger = logging.getLogger(__name__)


class VigilAgent:
    """
    Watches the research landscape for user-defined topics,
    tracking trends and surfacing relevant works.
    """

    def __init__(self):
        """Initialize the Vigil agent."""
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        """Create the LangGraph workflow for AlithiaVigil."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("scan_sources", scan_sources_node)
        workflow.add_node("filter_results", filter_results_node)
        workflow.add_node("send_alert", send_alert_node)

        # Define edges (linear workflow)
        workflow.add_edge("scan_sources", "filter_results")
        workflow.add_edge("filter_results", "send_alert")

        # Set entry and exit points
        workflow.set_entry_point("scan_sources")
        workflow.set_finish_point("send_alert")

        return workflow.compile()

    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Vigil agent with a given configuration.

        Args:
            config: Configuration dictionary with topics to monitor.

        Returns:
            Final state dictionary with results.
        """
        logger.info("Starting AlithiaVigil workflow...")
        initial_state = AgentState(profile=None, debug_mode=config.get("debug", False))
        # In a real implementation, a Vigil-specific profile/config would be used.
        # For now, we pass a minimal state.

        try:
            final_state = self.workflow.invoke(initial_state, config={"recursion_limit": 5})
            logger.info(f"Workflow completed. Final state: {final_state.get('current_step')}")
            return {"success": True, "summary": final_state}
        except Exception as e:
            logger.error(f"AlithiaVigil workflow failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
