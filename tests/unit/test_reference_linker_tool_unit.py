import numpy as np
import pytest

from alithia.core.tools.models import BibliographyEntry, ParagraphElement, Section, StructuredPaper
from alithia.core.tools.reference_linker import ReferenceLinkerTool, ReferenceLinkerInput


class DummyEmbeddingService:
    def embed_texts(self, texts):
        # Simple deterministic embeddings based on length
        vecs = np.array([[len(t) / 100.0, 1.0] for t in texts], dtype=float)
        # normalize
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.clip(norms, 1e-9, None)

    def rerank(self, query, candidates, top_k=8):
        return candidates


def build_sample_paper():
    para1 = ParagraphElement(element_id="p1", text="Discussed methods [1].")
    para2 = ParagraphElement(element_id="p2", text="Background details and survey.")
    para3 = ParagraphElement(element_id="p3", text="We follow previous work [2, 3].")
    section = Section(section_number="1", title="Intro", content=[para1, para2, para3])
    bib = [
        BibliographyEntry(ref_id="[1]", full_citation="Ref One"),
        BibliographyEntry(ref_id="[2]", full_citation="Ref Two"),
        BibliographyEntry(ref_id="[3]", full_citation="Ref Three"),
    ]
    return StructuredPaper(paper_id="abc", sections=[section], bibliography=bib)


def test_reference_linker_snippet_mode(monkeypatch):
    paper = build_sample_paper()
    tool = ReferenceLinkerTool(embedding_service=DummyEmbeddingService())
    out = tool.execute(ReferenceLinkerInput(source_paper=paper, query="As in [1] we do X."))
    ids = {r.ref_id for r in out.references}
    assert "[1]" in ids and len(ids) == 1


def test_reference_linker_topic_mode(monkeypatch):
    paper = build_sample_paper()
    tool = ReferenceLinkerTool(embedding_service=DummyEmbeddingService())
    out = tool.execute(ReferenceLinkerInput(source_paper=paper, query="previous work", top_k=2))
    ids = {r.ref_id for r in out.references}
    # From para3 citations
    assert "[2]" in ids and "[3]" in ids