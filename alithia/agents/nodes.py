"""
Agent nodes for the research agent workflow.
"""

import logging

from ..utils.arxiv_client import get_arxiv_papers
from ..utils.email_utils import construct_email_content, send_email
from ..utils.llm_utils import extract_affiliations, generate_tldr, get_code_url, get_llm
from ..utils.recommender import rerank_papers
from ..utils.zotero_client import filter_corpus, get_zotero_corpus
from .state import AgentState

logger = logging.getLogger(__name__)


def profile_analysis_node(state: AgentState) -> dict:
    """
    Initialize and analyze user research profile.

    Args:
        state: Current agent state

    Returns:
        Dictionary with updated state fields
    """
    logger.info("Analyzing user profile...")

    if not state.profile:
        state.add_error("No profile provided")
        return {"current_step": "profile_analysis_error"}

    # Validate profile
    errors = state.profile.validate()
    if errors:
        for error in errors:
            state.add_error(error)
        return {"current_step": "profile_validation_error"}

    logger.info(f"Profile validated for user: {state.profile.zotero_id}")
    return {"current_step": "profile_analysis_complete"}


def data_collection_node(state: AgentState) -> dict:
    """
    Collect papers from ArXiv and Zotero.

    Args:
        state: Current agent state

    Returns:
        Dictionary with updated state fields
    """
    logger.info("Collecting data from ArXiv and Zotero...")

    if not state.profile:
        state.add_error("No profile available for data collection")
        return {"current_step": "data_collection_error"}

    try:
        # Get Zotero corpus
        logger.info("Retrieving Zotero corpus...")
        corpus = get_zotero_corpus(state.profile.zotero_id, state.profile.zotero_key)
        logger.info(f"Retrieved {len(corpus)} papers from Zotero")

        # Apply ignore patterns
        if state.profile.ignore_patterns:
            ignore_patterns = "\n".join(state.profile.ignore_patterns)
            logger.info(f"Applying ignore patterns: {ignore_patterns}")
            corpus = filter_corpus(corpus, ignore_patterns)
            logger.info(f"Filtered corpus: {len(corpus)} papers remaining")

        # Get ArXiv papers
        logger.info("Retrieving ArXiv papers...")
        papers = get_arxiv_papers(state.profile.arxiv_query, state.debug_mode)
        logger.info(f"Retrieved {len(papers)} papers from ArXiv")

        return {"discovered_papers": papers, "zotero_corpus": corpus, "current_step": "data_collection_complete"}

    except Exception as e:
        state.add_error(f"Data collection failed: {str(e)}")
        return {"current_step": "data_collection_error"}


def relevance_assessment_node(state: AgentState) -> dict:
    """
    Score papers based on relevance to user's research.

    Args:
        state: Current agent state

    Returns:
        Dictionary with updated state fields
    """
    logger.info("Assessing paper relevance...")

    if not state.discovered_papers:
        logger.info("No papers discovered")
        return {"current_step": "relevance_assessment_complete"}

    if not state.zotero_corpus:
        logger.warning("No Zotero corpus available, using basic scoring")
        from ..models.paper import ScoredPaper

        scored_papers = [
            ScoredPaper(paper=paper, score=5.0, relevance_factors={"basic": 5.0}) for paper in state.discovered_papers
        ]
    else:
        try:
            scored_papers = rerank_papers(state.discovered_papers, state.zotero_corpus)
            logger.info(f"Scored {len(scored_papers)} papers")

        except Exception as e:
            state.add_error(f"Relevance assessment failed: {str(e)}")
            # Fallback to basic scoring
            from ..models.paper import ScoredPaper

            scored_papers = [
                ScoredPaper(paper=paper, score=5.0, relevance_factors={"fallback": 5.0})
                for paper in state.discovered_papers
            ]

    # Apply paper limit
    if state.profile and state.profile.max_papers > 0:
        scored_papers = scored_papers[: state.profile.max_papers]
        logger.info(f"Limited to {len(scored_papers)} papers")

    return {"scored_papers": scored_papers, "current_step": "relevance_assessment_complete"}


def content_generation_node(state: AgentState) -> dict:
    """
    Generate TLDR summaries and email content.

    Args:
        state: Current agent state

    Returns:
        Dictionary with updated state fields
    """
    logger.info("Generating content...")

    if not state.scored_papers:
        logger.info("No papers to process")
        return {"current_step": "content_generation_complete"}

    if not state.profile:
        state.add_error("No profile available for content generation")
        return {"current_step": "content_generation_error"}

    try:
        llm = get_llm(state.profile)

        # Generate TLDR and enrich paper data
        for scored_paper in state.scored_papers:
            paper = scored_paper.paper

            # Generate TLDR
            if not paper.tldr:
                paper.tldr = generate_tldr(paper, llm)

            # Extract affiliations
            if not paper.affiliations:
                paper.affiliations = extract_affiliations(paper, llm)

            # Get code URL
            if not paper.code_url:
                paper.code_url = get_code_url(paper)

        # Construct email content
        email_content = construct_email_content(state.scored_papers)

        logger.info("Content generation complete")
        return {"email_content": email_content, "current_step": "content_generation_complete"}

    except Exception as e:
        state.add_error(f"Content generation failed: {str(e)}")
        return {"current_step": "content_generation_error"}


def communication_node(state: AgentState) -> dict:
    """
    Send email with recommendations.

    Args:
        state: Current agent state

    Returns:
        Dictionary with updated state fields
    """
    logger.info("Preparing email delivery...")

    if not state.profile:
        state.add_error("No profile available for email delivery")
        return {"current_step": "communication_error"}

    # Check if we should send empty email
    if not state.email_content or (hasattr(state.email_content, "is_empty") and state.email_content.is_empty()):
        if not state.profile.send_empty:
            logger.info("No papers found and SEND_EMPTY=False, skipping email")
            return {"current_step": "workflow_complete"}
        else:
            logger.info("No papers found but SEND_EMPTY=True, sending empty email")

    try:
        # Send email
        success = send_email(
            sender=state.profile.sender_email,
            receiver=state.profile.receiver_email,
            password=state.profile.sender_password,
            smtp_server=state.profile.smtp_server,
            smtp_port=state.profile.smtp_port,
            html_content=state.email_content
            if isinstance(state.email_content, str)
            else state.email_content.html_content
            if state.email_content
            else "",
        )

        if success:
            logger.info("Email sent successfully")
            return {"current_step": "workflow_complete"}
        else:
            state.add_error("Email delivery failed")
            return {"current_step": "communication_error"}

    except Exception as e:
        state.add_error(f"Email delivery failed: {str(e)}")
        return {"current_step": "communication_error"}
