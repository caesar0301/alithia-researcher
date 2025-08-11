from unittest.mock import MagicMock, patch

import os
import pytest

from alithia.core.llm_utils import get_llm
from alithia.core.profile import ResearchProfile


@pytest.mark.unit
def test_get_llm_sets_env_and_model():
    profile = ResearchProfile(
        zotero_id="z",
        zotero_key="k",
        use_llm_api=True,
        openai_api_key="secret",
        openai_api_base="http://base",
        model_name="gpt-x",
    )

    fake_client = MagicMock()
    with patch("alithia.core.llm_utils.get_llm_client", return_value=fake_client) as mock_get:
        llm = get_llm(profile)

    assert os.environ.get("OPENAI_API_KEY") == "secret"
    assert os.environ.get("OPENAI_BASE_URL") == "http://base"
    assert fake_client.chat_model == "gpt-x"
    # called with provider openai
    mock_get.assert_called_with(provider="openai")