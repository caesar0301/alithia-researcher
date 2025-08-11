"""
LLM utilities for content generation using cogents.common.llm.
"""

import logging
import os

from cogents.common.llm import get_llm_client

from .profile import ResearchProfile

logger = logging.getLogger(__name__)


def get_llm(profile: ResearchProfile):
    """
    Get LLM instance based on profile configuration.

    Args:
        profile: ResearchProfile instance

    Returns:
        LLM client instance
    """
    # Configure API settings
    if profile.openai_api_key:
        os.environ["OPENAI_API_KEY"] = profile.openai_api_key
        if profile.openai_api_base:
            os.environ["OPENAI_BASE_URL"] = profile.openai_api_base

    try:
        llm = get_llm_client(provider="openai", chat_model=profile.model_name)
        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize LLM client: {e}")
        raise e
