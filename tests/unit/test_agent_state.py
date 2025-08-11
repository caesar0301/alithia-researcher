import pytest

from alithia.core.agent_state import AgentState
from alithia.core.paper import ArxivPaper, ScoredPaper


@pytest.mark.unit
def test_add_error_and_update_metric_and_summary():
    state = AgentState()

    # Add error and metric
    state.add_error("something went wrong")
    state.update_metric("latency_ms", 123.4)

    # Add some papers to counts
    paper = ArxivPaper(
        title="t",
        summary="s",
        authors=["a"],
        arxiv_id="1234.5678",
        pdf_url="http://x",
    )
    state.discovered_papers.append(paper)
    state.scored_papers.append(ScoredPaper(paper=paper, score=7.5))

    summary = state.get_summary()

    assert summary["current_step"] == state.current_step
    assert summary["papers_discovered"] == 1
    assert summary["papers_scored"] == 1
    assert summary["errors"] == 1
    assert summary["metrics"]["latency_ms"] == 123.4