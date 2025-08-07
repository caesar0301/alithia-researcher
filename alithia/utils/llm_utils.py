"""
LLM utilities for content generation using cogents.common.llm.
"""

import logging
import os
import re
from typing import List, Optional

import requests
import tiktoken
from cogents.common.llm import get_llm_client
from requests.adapters import HTTPAdapter, Retry

from ..models.paper import ArxivPaper

logger = logging.getLogger(__name__)


def get_llm(profile):
    """
    Get LLM instance based on profile configuration.

    Args:
        profile: ResearchProfile instance

    Returns:
        LLM client instance
    """
    # Set environment variables for OpenRouter if using API
    if profile.use_llm_api and profile.openai_api_key:
        os.environ["OPENROUTER_API_KEY"] = profile.openai_api_key
        if profile.openai_api_base:
            os.environ["OPENAI_BASE_URL"] = profile.openai_api_base

    try:
        llm = get_llm_client()

        # Override model if specified in profile
        if profile.model_name:
            llm.chat_model = profile.model_name

        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize LLM client: {e}")
        raise e


def extract_tex_content(paper: ArxivPaper) -> Optional[Dict[str, str]]:
    """
    Extract LaTeX content from paper source.

    Args:
        paper: ArxivPaper instance

    Returns:
        Dictionary with extracted LaTeX content or None if extraction fails
    """
    # For now, return mock content based on paper metadata
    return {"all": f"\\title{{{paper.title}}}\n\\begin{{abstract}}{paper.summary}\\end{{abstract}}"}


def generate_tldr(paper: ArxivPaper, llm) -> str:
    """
    Generate TLDR summary for a paper.

    Args:
        paper: ArxivPaper to summarize
        llm: LLM instance for generation

    Returns:
        TLDR summary string
    """
    introduction = ""
    conclusion = ""

    # Extract LaTeX content
    tex_content = extract_tex_content(paper)
    if tex_content and tex_content.get("all"):
        content = tex_content["all"]

        # Clean content
        content = re.sub(r"~?\\cite.?\{.*?\}", "", content)
        content = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", content, flags=re.DOTALL)
        content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", content, flags=re.DOTALL)

        # Extract introduction and conclusion
        intro_match = re.search(
            r"\\section\{Introduction\}.*?(\\section|\\end\{document\}|\\bibliography|\\appendix|$)",
            content,
            flags=re.DOTALL,
        )
        if intro_match:
            introduction = intro_match.group(0)

        conclusion_match = re.search(
            r"\\section\{Conclusion\}.*?(\\section|\\end\{document\}|\\bibliography|\\appendix|$)",
            content,
            flags=re.DOTALL,
        )
        if conclusion_match:
            conclusion = conclusion_match.group(0)

    # Prepare prompt
    prompt = f"""Given the title, abstract, introduction and the conclusion (if any) of a paper in latex format, generate a one-sentence TLDR summary in {llm.lang}:

\\title{{{paper.title}}}
\\begin{{abstract}}{paper.summary}\\end{{abstract}}
{introduction}
{conclusion}"""

    # Truncate if too long
    enc = tiktoken.encoding_for_model("gpt-4o")
    prompt_tokens = enc.encode(prompt)
    if len(prompt_tokens) > 4000:
        prompt_tokens = prompt_tokens[:4000]
        prompt = enc.decode(prompt_tokens)

    # Generate summary
    messages = [
        {
            "role": "system",
            "content": "You are an assistant who perfectly summarizes scientific paper, and gives the core idea of the paper to the user.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        return llm.chat_completion(messages, temperature=0)
    except Exception as e:
        logger.warning(f"Failed to generate TLDR: {e}")
        return f"Failed to generate TLDR for paper: {paper.title}"


def extract_affiliations(paper: ArxivPaper, llm) -> Optional[List[str]]:
    """
    Extract author affiliations from paper.

    Args:
        paper: ArxivPaper to analyze
        llm: LLM instance for extraction

    Returns:
        List of affiliations or None if extraction fails
    """
    tex_content = extract_tex_content(paper)
    if not tex_content or not tex_content.get("all"):
        return None

    content = tex_content["all"]

    # Find author information region
    possible_regions = [r"\\author.*?\\maketitle", r"\\begin{document}.*?\\begin{abstract}"]

    information_region = None
    for pattern in possible_regions:
        match = re.search(pattern, content, flags=re.DOTALL)
        if match:
            information_region = match.group(0)
            break

    if not information_region:
        return None

    prompt = f"""Given the author information of a paper in latex format, extract the affiliations of the authors in a python list format, which is sorted by the author order. If there is no affiliation found, return an empty list '[]'. Following is the author information:

{information_region}"""

    # Truncate if too long
    enc = tiktoken.encoding_for_model("gpt-4o")
    prompt_tokens = enc.encode(prompt)
    if len(prompt_tokens) > 4000:
        prompt_tokens = prompt_tokens[:4000]
        prompt = enc.decode(prompt_tokens)

    messages = [
        {
            "role": "system",
            "content": "You are an assistant who perfectly extracts affiliations of authors from the author information of a paper. You should return a python list of affiliations sorted by the author order, like ['TsingHua University','Peking University']. If an affiliation is consisted of multi-level affiliations, like 'Department of Computer Science, TsingHua University', you should return the top-level affiliation 'TsingHua University' only. Do not contain duplicated affiliations. If there is no affiliation found, you should return an empty list [ ]. You should only return the final list of affiliations, and do not return any intermediate results.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        result = llm.chat_completion(messages, temperature=0)
        affiliations_match = re.search(r"\[.*?\]", result, flags=re.DOTALL)
        if affiliations_match:
            affiliations = eval(affiliations_match.group(0))
            # Remove duplicates and convert to strings
            unique_affiliations = list(set(str(a) for a in affiliations))
            return unique_affiliations
    except Exception as e:
        logger.warning(f"Failed to extract affiliations: {e}")

    return None


def get_code_url(paper: ArxivPaper) -> Optional[str]:
    """
    Find code repository URL for a paper.

    Args:
        paper: ArxivPaper to search for

    Returns:
        Code repository URL or None if not found
    """
    try:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1)
        session.mount("https://", HTTPAdapter(max_retries=retries))

        # Search Papers with Code
        response = session.get(f"https://paperswithcode.com/api/v1/papers/?arxiv_id={paper.arxiv_id}")
        response.raise_for_status()

        paper_list = response.json()
        if paper_list.get("count", 0) == 0:
            return None

        paper_id = paper_list["results"][0]["id"]

        # Get repositories
        response = session.get(f"https://paperswithcode.com/api/v1/papers/{paper_id}/repositories/")
        response.raise_for_status()

        repo_list = response.json()
        if repo_list.get("count", 0) == 0:
            return None

        return repo_list["results"][0]["url"]

    except Exception as e:
        logger.warning(f"Failed to get code URL: {e}")
        return None
