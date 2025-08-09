"""
LLM utilities for content generation using cogents.common.llm.
"""

import logging
import os
import re
import tarfile
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional
from urllib.error import HTTPError

import requests
import tiktoken
from cogents.common.llm import get_llm_client
from requests.adapters import HTTPAdapter, Retry

from .paper import ArxivPaper
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
    if profile.use_llm_api and profile.openai_api_key:
        os.environ["OPENAI_API_KEY"] = profile.openai_api_key
        if profile.openai_api_base:
            os.environ["OPENAI_BASE_URL"] = profile.openai_api_base

    try:
        llm = get_llm_client(provider="openai")

        # Set model if specified
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
    with ExitStack() as stack:
        tmpdirname = stack.enter_context(TemporaryDirectory())
        try:
            if not paper.arxiv_result:
                logger.warning(f"No arxiv result available for {paper.arxiv_id}, skipping source analysis")
                return None
            file = paper.arxiv_result.download_source(dirpath=tmpdirname)
        except HTTPError as e:
            if e.code == 404:
                # Source files don't exist (normal)
                logger.warning(f"Source for {paper.arxiv_id} not found (404). Skipping source analysis.")
                return None
            else:
                # Other HTTP errors may be temporary
                logger.error(f"HTTP Error {e.code} when downloading source for {paper.arxiv_id}: {e.reason}")
                raise
        try:
            tar = stack.enter_context(tarfile.open(file))
        except tarfile.ReadError:
            logger.debug(f"Failed to find main tex file of {paper.arxiv_id}: Not a tar file.")
            return None

        tex_files = [f for f in tar.getnames() if f.endswith(".tex")]
        if len(tex_files) == 0:
            logger.debug(f"Failed to find main tex file of {paper.arxiv_id}: No tex file.")
            return None

        bbl_file = [f for f in tar.getnames() if f.endswith(".bbl")]
        match len(bbl_file):
            case 0:
                if len(tex_files) > 1:
                    logger.debug(
                        f"Cannot find main tex file of {paper.arxiv_id} from bbl: There are multiple tex files while no bbl file."
                    )
                    main_tex = None
                else:
                    main_tex = tex_files[0]
            case 1:
                main_name = bbl_file[0].replace(".bbl", "")
                main_tex = f"{main_name}.tex"
                if main_tex not in tex_files:
                    logger.debug(
                        f"Cannot find main tex file of {paper.arxiv_id} from bbl: The bbl file does not match any tex file."
                    )
                    main_tex = None
            case _:
                logger.debug(f"Cannot find main tex file of {paper.arxiv_id} from bbl: There are multiple bbl files.")
                main_tex = None
        if main_tex is None:
            logger.debug(
                f"Trying to choose tex file containing the document block as main tex file of {paper.arxiv_id}"
            )
        # Process all tex files
        file_contents = {}
        for t in tex_files:
            f = tar.extractfile(t)
            content = f.read().decode("utf-8", errors="ignore")
            # Clean content
            content = re.sub(r"%.*\n", "\n", content)
            content = re.sub(r"\\begin{comment}.*?\\end{comment}", "", content, flags=re.DOTALL)
            content = re.sub(r"\\iffalse.*?\\fi", "", content, flags=re.DOTALL)
            content = re.sub(r"\n+", "\n", content)
            content = re.sub(r"\\\\", "", content)
            content = re.sub(r"[ \t\r\f]{3,}", " ", content)
            if main_tex is None and re.search(r"\\begin\{document\}", content):
                main_tex = t
                logger.debug(f"Choose {t} as main tex file of {paper.arxiv_id}")
            file_contents[t] = content

        if main_tex is not None:
            main_source: str = file_contents[main_tex]
            # Resolve includes
            include_files = re.findall(r"\\input\{(.+?)\}", main_source) + re.findall(
                r"\\include\{(.+?)\}", main_source
            )
            for f in include_files:
                if not f.endswith(".tex"):
                    file_name = f + ".tex"
                else:
                    file_name = f
                main_source = main_source.replace(f"\\input{{{f}}}", file_contents.get(file_name, ""))
            file_contents["all"] = main_source
        else:
            logger.debug(
                f"Failed to find main tex file of {paper.arxiv_id}: No tex file containing the document block."
            )
            file_contents["all"] = None
        return file_contents


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

    # Get LaTeX content
    tex_content = extract_tex_content(paper)
    if tex_content is not None:
        content = tex_content.get("all")
        if content is None:
            content = "\n".join(tex_content.values())
        # Clean content
        content = re.sub(r"~?\\cite.?\{.*?\}", "", content)
        content = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", content, flags=re.DOTALL)
        content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", content, flags=re.DOTALL)
        # Extract sections
        match = re.search(
            r"\\section\{Introduction\}.*?(\\section|\\end\{document\}|\\bibliography|\\appendix|$)",
            content,
            flags=re.DOTALL,
        )
        if match:
            introduction = match.group(0)
        match = re.search(
            r"\\section\{Conclusion\}.*?(\\section|\\end\{document\}|\\bibliography|\\appendix|$)",
            content,
            flags=re.DOTALL,
        )
        if match:
            conclusion = match.group(0)

    prompt = f"""Given the title, abstract, introduction and the conclusion (if any) of a paper in latex format, generate a one-sentence TLDR summary in English:

\\title{{{paper.title}}}
\\begin{{abstract}}{paper.summary}\\end{{abstract}}
{introduction}
{conclusion}"""

    # Truncate prompt if too long
    enc = tiktoken.encoding_for_model("gpt-4o")
    prompt_tokens = enc.encode(prompt)
    prompt_tokens = prompt_tokens[:4000]
    prompt = enc.decode(prompt_tokens)

    tldr = llm.generate(
        messages=[
            {
                "role": "system",
                "content": "You are an assistant who perfectly summarizes scientific paper, and gives the core idea of the paper to the user.",
            },
            {"role": "user", "content": prompt},
        ]
    )
    return tldr


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
    if tex_content is not None:
        content = tex_content.get("all")
        if content is None:
            content = "\n".join(tex_content.values())
        # Find author info
        possible_regions = [r"\\author.*?\\maketitle", r"\\begin{document}.*?\\begin{abstract}"]
        matches = [re.search(p, content, flags=re.DOTALL) for p in possible_regions]
        match = next((m for m in matches if m), None)
        if match:
            information_region = match.group(0)
        else:
            logger.debug(f"Failed to extract affiliations of {paper.arxiv_id}: No author information found.")
            return None
        prompt = f"Given the author information of a paper in latex format, extract the affiliations of the authors in a python list format, which is sorted by the author order. If there is no affiliation found, return an empty list '[]'. Following is the author information:\n{information_region}"
        # Truncate prompt if too long
        enc = tiktoken.encoding_for_model("gpt-4o")
        prompt_tokens = enc.encode(prompt)
        prompt_tokens = prompt_tokens[:4000]
        prompt = enc.decode(prompt_tokens)
        affiliations = llm.generate(
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant who perfectly extracts affiliations of authors from the author information of a paper. You should return a python list of affiliations sorted by the author order, like ['TsingHua University','Peking University']. If an affiliation is consisted of multi-level affiliations, like 'Department of Computer Science, TsingHua University', you should return the top-level affiliation 'TsingHua University' only. Do not contain duplicated affiliations. If there is no affiliation found, you should return an empty list [ ]. You should only return the final list of affiliations, and do not return any intermediate results.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        try:
            affiliations = re.search(r"\[.*?\]", affiliations, flags=re.DOTALL).group(0)
            affiliations = eval(affiliations)
            affiliations = list(set(affiliations))
            affiliations = [str(a) for a in affiliations]
        except Exception as e:
            logger.debug(f"Failed to extract affiliations of {paper.arxiv_id}: {e}")
            return None
        return affiliations


def get_code_url(paper: ArxivPaper) -> Optional[str]:
    """
    Find code repository URL for a paper.

    Args:
        paper: ArxivPaper to search for

    Returns:
        Code repository URL or None if not found
    """
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1)
    s.mount("https://", HTTPAdapter(max_retries=retries))
    try:
        paper_list = s.get(f"https://paperswithcode.com/api/v1/papers/?arxiv_id={paper.arxiv_id}").json()
    except Exception as e:
        logger.debug(f"Error when searching {paper.arxiv_id}: {e}")
        return None

    if paper_list.get("count", 0) == 0:
        return None
    paper_id = paper_list["results"][0]["id"]

    try:
        repo_list = s.get(f"https://paperswithcode.com/api/v1/papers/{paper_id}/repositories/").json()
    except Exception as e:
        logger.debug(f"Error when searching {paper.arxiv_id}: {e}")
        return None
    if repo_list.get("count", 0) == 0:
        return None
    return repo_list["results"][0]["url"]
