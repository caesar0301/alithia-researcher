"""
Paper data models for the Alithia research agent.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ArxivPaper:
    """Represents an ArXiv paper with all relevant metadata."""

    title: str
    summary: str
    authors: List[str]
    arxiv_id: str
    pdf_url: str
    code_url: Optional[str] = None
    affiliations: Optional[List[str]] = None
    tldr: Optional[str] = None
    score: Optional[float] = None
    published_date: Optional[datetime] = None

    @classmethod
    def from_arxiv_result(cls, paper_result) -> "ArxivPaper":
        """Create ArxivPaper from arxiv.Result object."""
        arxiv_id = re.sub(r"v\d+$", "", paper_result.get_short_id())

        return cls(
            title=paper_result.title,
            summary=paper_result.summary,
            authors=[author.name for author in paper_result.authors],
            arxiv_id=arxiv_id,
            pdf_url=paper_result.pdf_url,
            published_date=paper_result.published,
        )


@dataclass
class ScoredPaper:
    """Represents a paper with relevance score."""

    paper: ArxivPaper
    score: float
    relevance_factors: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Update the paper's score."""
        self.paper.score = self.score


@dataclass
class EmailContent:
    """Represents the content for email delivery."""

    subject: str
    html_content: str
    papers: List[ScoredPaper]
    generated_at: datetime = field(default_factory=datetime.now)

    def is_empty(self) -> bool:
        """Check if email has no papers."""
        return len(self.papers) == 0
