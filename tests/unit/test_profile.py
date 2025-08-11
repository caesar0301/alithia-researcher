import pytest

from alithia.core.profile import ResearchProfile


@pytest.mark.unit
def test_profile_from_config_defaults_and_values():
    cfg = {
        "zotero_id": "zid",
        "zotero_key": "zkey",
        "research_interests": ["AI"],
        "expertise_level": "advanced",
        "language": "English",
        "max_paper_num": 30,
        "send_empty": True,
        "zotero_ignore": "a\n b\n",
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "sender": "sender@example.com",
        "sender_password": "pass",
        "receiver": "recv@example.com",
        "use_llm_api": True,
        "openai_api_key": "ok",
        "openai_api_base": "http://base",
        "model_name": "gpt-x",
        "arxiv_query": "cs.AI",
    }
    p = ResearchProfile.from_config(cfg)

    assert p.zotero_id == "zid"
    assert p.max_papers == 30
    assert p.send_empty is True
    assert p.ignore_patterns == ["a", " b"]
    assert p.model_name == "gpt-x"


@pytest.mark.unit
def test_profile_validate_missing_fields():
    p = ResearchProfile(
        zotero_id="",
        zotero_key="",
    )
    errs = p.validate()
    assert "Zotero ID is required" in errs
    assert "Zotero API key is required" in errs
    assert "SMTP server is required" in errs
    assert "Sender email is required" in errs
    assert "Receiver email is required" in errs


@pytest.mark.unit
def test_profile_validate_llm_requires_key():
    p = ResearchProfile(zotero_id="a", zotero_key="b", use_llm_api=True)
    errs = p.validate()
    assert "OpenAI API key is required when using LLM API" in errs
