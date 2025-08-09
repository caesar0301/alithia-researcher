"""
Placeholder nodes for the AlithiaVigil agent workflow.
"""

import logging

from alithia.core.agent_state import AgentState

logger = logging.getLogger(__name__)


def scan_sources_node(state: AgentState) -> dict:
    """
    Placeholder node for scanning various sources.
    """
    logger.info(">>> Executing Node: scan_sources <<<")
    logger.info("Scanning sources like ArXiv, Twitter, blogs...")
    # In a real implementation, this would involve API calls and data fetching.
    # For now, we'll just populate with dummy data.
    discovered_items = [
        {"source": "ArXiv", "title": "Paper on Topic A"},
        {"source": "Twitter", "content": "Tweet about Topic B"},
    ]
    return {"discovered_papers": discovered_items, "current_step": "scan_complete"}


def filter_results_node(state: AgentState) -> dict:
    """
    Placeholder node for filtering results based on relevance.
    """
    logger.info(">>> Executing Node: filter_results <<<")
    logger.info("Filtering discovered items based on user interests...")
    # This would use embedding-based filtering.
    # We'll just pass the data through.
    scored_papers = state.get("discovered_papers", [])
    return {"scored_papers": scored_papers, "current_step": "filter_complete"}


def send_alert_node(state: AgentState) -> dict:
    """
    Placeholder node for sending alerts to the user.
    """
    logger.info(">>> Executing Node: send_alert <<<")
    logger.info("Sending alert to user via CLI, email, or Slack...")
    # This would format and send a digest of the findings.
    num_items = len(state.get("scored_papers", []))
    logger.info(f"Alert content: Found {num_items} relevant items.")
    return {"current_step": "workflow_complete"}
