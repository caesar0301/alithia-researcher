"""
Placeholder nodes for the AlithiaLens agent workflow.
"""

import logging
from typing import Literal

from alithia.core.state import AgentState

logger = logging.getLogger(__name__)


def get_user_input_node(state: AgentState) -> dict:
    """
    Placeholder node for getting user input.
    In a real CLI, this would block and wait for `input()`.
    For this skeleton, we'll simulate a sequence of inputs.
    """
    logger.info(">>> Executing Node: get_user_input <<<")

    # Simulate a conversation flow
    if state.get("last_node") is None:
        # First turn
        user_input = state.get("user_input") or "load 1234.56789"
    elif state.get("last_node") == "load_paper":
        user_input = "What is the main contribution?"
    elif state.get("last_node") == "process_query":
        # End the conversation after one question
        user_input = "exit"
    else:
        user_input = "exit"

    logger.info(f"Simulated user input: '{user_input}'")
    return {"user_input": user_input}


def route_query_node(state: AgentState) -> Literal["load", "interact", "exit"]:
    """
    Routes the user's query to the appropriate handler.
    """
    logger.info(">>> Executing Node: route_query <<<")
    user_input = state.get("user_input", "").lower()

    if user_input.startswith("load"):
        logger.info("Routing to: load_paper")
        return "load"
    elif user_input in ["exit", "quit"]:
        logger.info("Routing to: exit")
        return "exit"
    else:
        logger.info("Routing to: process_query")
        return "interact"


def load_paper_node(state: AgentState) -> dict:
    """
    Placeholder node for loading and processing a paper.
    """
    logger.info(">>> Executing Node: load_paper <<<")
    paper_id = state.get("user_input", "").replace("load ", "")
    logger.info(f"Loading and processing paper: {paper_id}")
    # In a real implementation, this would fetch the paper, parse it,
    # and store its content/embeddings in the state.
    return {
        "current_paper": {"id": paper_id, "title": f"Paper {paper_id}"},
        "last_node": "load_paper",
    }


def process_query_node(state: AgentState) -> dict:
    """
    Placeholder node for answering a user's question about the paper.
    """
    logger.info(">>> Executing Node: process_query <<<")
    query = state.get("user_input")
    paper = state.get("current_paper", {})
    logger.info(f"Answering question '{query}' about paper '{paper.get('title', 'N/A')}'")
    # This would involve semantic search over the paper's content and LLM-based generation.
    response = "The main contribution is a novel method for something important."
    logger.info(f"Generated response: '{response}'")
    return {"last_response": response, "last_node": "process_query"}
