from typing import Any, Dict

from pydantic import BaseModel


class ZoteroConnection(BaseModel):
    """Zotero connection."""

    zotero_id: str
    zotero_key: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ZoteroConnection":
        """Create ZoteroConnection from configuration dictionary."""
        return cls(zotero_id=config.get("zotero_id", ""), zotero_key=config.get("zotero_key", ""))


class EmailConnection(BaseModel):
    """Email connection."""

    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    receiver_email: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "EmailConnection":
        """Create EmailConnection from configuration dictionary."""
        return cls(
            smtp_server=config.get("smtp_server", ""),
            smtp_port=config.get("smtp_port", 587),
            sender_email=config.get("sender_email", ""),
            sender_password=config.get("sender_password", ""),
            receiver_email=config.get("receiver_email", ""),
        )


class GithubConnection(BaseModel):
    """Github connection."""

    github_username: str
    github_token: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "GithubConnection":
        """Create GithubConnection from configuration dictionary."""
        return cls(github_username=config.get("github_username", ""), github_token=config.get("github_token", ""))


class GoogleScholarConnection(BaseModel):
    """Google Scholar connection."""

    google_scholar_id: str
    google_scholar_token: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "GoogleScholarConnection":
        """Create GoogleScholarConnection from configuration dictionary."""
        return cls(
            google_scholar_id=config.get("google_scholar_id", ""),
            google_scholar_token=config.get("google_scholar_token", ""),
        )


class XConnection(BaseModel):
    """X connection."""

    x_username: str
    x_token: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "XConnection":
        """Create XConnection from configuration dictionary."""
        return cls(x_username=config.get("x_username", ""), x_token=config.get("x_token", ""))


class LLMConnection(BaseModel):
    """LLM connection."""

    openai_api_key: str
    openai_api_base: str
    model_name: str

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMConnection":
        """Create LLMConnection from configuration dictionary."""
        return cls(
            openai_api_key=config.get("openai_api_key", ""),
            openai_api_base=config.get("openai_api_base", "https://api.openai.com/v1"),
            model_name=config.get("model_name", "gpt-4o"),
        )
