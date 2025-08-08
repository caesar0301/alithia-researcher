"""
User profile and configuration models for the Alithia research agent.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchProfile(BaseModel):
    """Represents a user's research profile and preferences."""

    zotero_id: str
    zotero_key: str
    research_interests: List[str] = Field(default_factory=list)
    expertise_level: str = "intermediate"
    language: str = "English"
    max_papers: int = 50
    send_empty: bool = False
    ignore_patterns: List[str] = Field(default_factory=list)

    # SMTP Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None
    receiver_email: Optional[str] = None

    # LLM Configuration
    use_llm_api: bool = False
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o"

    # ArXiv Configuration
    arxiv_query: str = "cs.AI+cs.CV+cs.LG+cs.CL"

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ResearchProfile":
        """Create ResearchProfile from configuration dictionary."""
        return cls(
            zotero_id=config.get("zotero_id", ""),
            zotero_key=config.get("zotero_key", ""),
            research_interests=config.get("research_interests", []),
            expertise_level=config.get("expertise_level", "intermediate"),
            language=config.get("language", "English"),
            max_papers=config.get("max_paper_num", 50),
            send_empty=config.get("send_empty", False),
            ignore_patterns=config.get("zotero_ignore", "").splitlines(),
            smtp_server=config.get("smtp_server"),
            smtp_port=config.get("smtp_port"),
            sender_email=config.get("sender"),
            sender_password=config.get("sender_password"),
            receiver_email=config.get("receiver"),
            use_llm_api=config.get("use_llm_api", False),
            openai_api_key=config.get("openai_api_key"),
            openai_api_base=config.get("openai_api_base", "https://api.openai.com/v1"),
            model_name=config.get("model_name", "gpt-4o"),
            arxiv_query=config.get("arxiv_query", "cs.AI+cs.CV+cs.LG+cs.CL"),
        )

    def validate(self) -> List[str]:
        """Validate the profile configuration."""
        errors = []

        if not self.zotero_id:
            errors.append("Zotero ID is required")
        if not self.zotero_key:
            errors.append("Zotero API key is required")
        if not self.smtp_server:
            errors.append("SMTP server is required")
        if not self.sender_email:
            errors.append("Sender email is required")
        if not self.receiver_email:
            errors.append("Receiver email is required")
        if self.use_llm_api and not self.openai_api_key:
            errors.append("OpenAI API key is required when using LLM API")

        return errors
