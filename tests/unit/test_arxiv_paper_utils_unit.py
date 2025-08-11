import re
from unittest.mock import Mock

import pytest

from alithia.core.arxiv_paper_utils import (
    ExtractAffiliationsTool,
    GenerateTLDRTool,
    GetCodeURLTool,
    extract_affiliations,
    generate_tldr,
    get_code_url,
)
from alithia.core.paper import ArxivPaper


@pytest.mark.unit
def test_extract_tex_content_no_arxiv_result_returns_none():
    p = ArxivPaper(title="t", summary="s", authors=["a"], arxiv_id="x", pdf_url="http://x")
    assert extract_tex_content(p) is None


@pytest.mark.unit
def test_generate_tldr_uses_llm_and_truncates_prompt():
    p = ArxivPaper(title="t" * 1000, summary="s" * 5000, authors=["a"], arxiv_id="x", pdf_url="http://x")
    fake_llm = Mock()
    fake_llm.chat_completion.return_value = "TLDR"

    with patch("alithia.core.arxiv_paper_utils.extract_tex_content", return_value=None), patch(
        "alithia.core.arxiv_paper_utils.tiktoken"
    ) as mock_tiktoken:
        mock_enc = Mock()
        mock_enc.encode.side_effect = lambda s: list(range(min(len(s), 8000)))
        mock_enc.decode.side_effect = lambda toks: "x" * len(toks)
        mock_tiktoken.encoding_for_model.return_value = mock_enc

        res = generate_tldr(p, fake_llm)
        assert res == "TLDR"
        fake_llm.chat_completion.assert_called()


@pytest.mark.unit
def test_extract_affiliations_parses_list():
    p = ArxivPaper(title="t", summary="s", authors=["a"], arxiv_id="x", pdf_url="http://x")

    # Provide fake tex with author information
    fake_tex = {
        "all": r"""\\author{Alice \\and Bob} \\maketitle""",
    }
    fake_llm = Mock()
    fake_llm.chat_completion.return_value = "['Inst A', 'Inst B']"

    with patch("alithia.core.arxiv_paper_utils.extract_tex_content", return_value=fake_tex), patch(
        "alithia.core.arxiv_paper_utils.tiktoken"
    ) as mock_tiktoken:
        mock_enc = Mock()
        mock_enc.encode.side_effect = lambda s: list(range(min(len(s), 8000)))
        mock_enc.decode.side_effect = lambda toks: "x" * len(toks)
        mock_tiktoken.encoding_for_model.return_value = mock_enc

        affs = extract_affiliations(p, fake_llm)
        assert set(affs) == {"Inst A", "Inst B"}


def test_generate_tldr_tool_wrapper(monkeypatch):
    paper = ArxivPaper(title="T", summary="S", authors=["A"], arxiv_id="1", pdf_url="u")

    class DummyLLM:
        def chat_completion(self, messages):
            return "TLDR"

    tool = GenerateTLDRTool()
    out = tool({"paper": paper, "llm": DummyLLM()})
    assert out.tldr == "TLDR"


def test_extract_affiliations_tool_wrapper(monkeypatch):
    paper = ArxivPaper(title="T", summary="S", authors=["A"], arxiv_id="1", pdf_url="u")

    class DummyLLM:
        def chat_completion(self, messages):
            return "['X University']"

    tool = ExtractAffiliationsTool()
    out = tool({"paper": paper, "llm": DummyLLM()})
    assert isinstance(out.affiliations, list)


def test_get_code_url_tool_wrapper(monkeypatch):
    paper = ArxivPaper(title="T", summary="S", authors=["A"], arxiv_id="1", pdf_url="u")
    # Monkeypatch get_code_url to avoid network
    monkeypatch.setattr(
        "alithia.core.arxiv_paper_utils.get_code_url", lambda p: "https://github.com/example/repo"
    )
    tool = GetCodeURLTool()
    out = tool({"paper": paper})
    assert out.url.endswith("/repo")
