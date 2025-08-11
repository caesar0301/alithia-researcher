from __future__ import annotations

from typing import Any, Dict, List, Optional

import arxiv
from pydantic import BaseModel

from .base import Tool, ToolInput, ToolOutput


class FindPaperInfoInput(ToolInput):
    title: str
    authors: Optional[List[str]] = None


class FindPaperInfoOutput(ToolOutput):
    metadata: Dict[str, Any]
    pdf_url: Optional[str] = None


class WebSearcherTool(Tool):
    InputModel = FindPaperInfoInput

    def __init__(self) -> None:
        super().__init__(
            name="core.web_searcher",
            description="Find paper metadata and PDF URL via academic sources (arXiv first)",
        )

    def execute(self, inputs: FindPaperInfoInput, **kwargs: Any) -> FindPaperInfoOutput:
        # Try arXiv exact title match first
        search = arxiv.Search(query=f'ti:"{inputs.title}"', max_results=5)
        client = arxiv.Client(num_retries=5)
        candidates = list(client.results(search))

        def normalize(s: Optional[str]) -> str:
            return (s or "").strip().lower()

        best = None
        for c in candidates:
            if normalize(c.title) == normalize(inputs.title):
                best = c
                break
        if best is None and candidates:
            best = candidates[0]

        if best is not None:
            authors = [a.name for a in best.authors]
            metadata = {
                "title": best.title,
                "authors": authors,
                "abstract": best.summary,
                "published": getattr(best, "published", None),
                "arxiv_id": best.get_short_id() if hasattr(best, "get_short_id") else None,
            }
            return FindPaperInfoOutput(metadata=metadata, pdf_url=best.pdf_url)

        # Fallback: return minimal metadata without URL
        return FindPaperInfoOutput(metadata={"title": inputs.title, "authors": inputs.authors or []}, pdf_url=None)

    # Convenience sub-tools as methods for tests and future chaining
    def find_paper_info(self, title: str, authors: Optional[List[str]] = None) -> FindPaperInfoOutput:
        return self.execute(FindPaperInfoInput(title=title, authors=authors))