"""
Main entry point for the Alithia research agent.
Replicates zotero-arxiv-daily functionality using agentic architecture.
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

from alithia.agents.arxrec.arxrec_agent import ArxrecAgent
from alithia.core.researcher.profile import ResearcherProfile

from .state import ArxrecConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_env(key: str, default=None):
    """
    Get environment variable, handling empty strings as None.

    Args:
        key: Environment variable key
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    value = os.environ.get(key)
    if value == "" or value is None:
        return default
    return value


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser with all necessary arguments."""
    parser = argparse.ArgumentParser(
        description="A personalized arXiv recommendation agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with environment variables
  python -m alithia.agents.arxrec
  
  # Run with configuration file
  python -m alithia.agents.arxrec --config config.json
        """,
    )
    # Optional arguments
    parser.add_argument("-c", "--config", type=str, help="Configuration file path (JSON)")

    return parser


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    import json

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config file {config_path}: {e}")
        sys.exit(1)


def build_config_from_envs() -> Dict[str, Any]:
    """
    Build configuration dictionary from environment variables.

    Returns:
        Configuration dictionary in nested format
    """
    config = {}

    # Map environment variables to nested config structure
    env_mapping = {
        # General settings
        "research_interests": "RESEARCH_INTERESTS",
        "expertise_level": "EXPERTISE_LEVEL",
        "language": "LANGUAGE",
        "email": "EMAIL",
        "debug": "DEBUG",
        # LLM settings
        "llm.openai_api_key": "OPENAI_API_KEY",
        "llm.openai_api_base": "OPENAI_API_BASE",
        "llm.model_name": "MODEL_NAME",
        # Zotero settings
        "zotero.zotero_id": "ZOTERO_ID",
        "zotero.zotero_key": "ZOTERO_KEY",
        # Email notification settings
        "email_notification.smtp_server": "SMTP_SERVER",
        "email_notification.smtp_port": "SMTP_PORT",
        "email_notification.sender_email": "SENDER",
        "email_notification.sender_password": "SENDER_PASSWORD",
        "email_notification.receiver_email": "RECEIVER",
        # Arxrec specific settings
        "arxrec.query": "ARXIV_QUERY",
        "arxrec.max_papers": "MAX_PAPER_NUM",
        "arxrec.send_empty": "SEND_EMPTY",
        "arxrec.ignore_patterns": "ZOTERO_IGNORE",
    }

    for config_key, env_key in env_mapping.items():
        value = get_env(env_key)
        if value is not None:
            # Convert string values to appropriate types
            if config_key in ["email_notification.smtp_port", "arxrec.max_papers"]:
                try:
                    value = int(value)
                except ValueError:
                    continue
            elif config_key in ["arxrec.send_empty", "debug"]:
                value = str(value).lower() in ["true", "1", "yes"]
            elif config_key == "arxrec.ignore_patterns" and value:
                # Convert comma-separated string to list
                value = [pattern.strip() for pattern in value.split(",") if pattern.strip()]
            elif config_key == "research_interests" and value:
                # Convert comma-separated string to list
                value = [interest.strip() for interest in value.split(",") if interest.strip()]

            # Set nested value
            _set_nested_value(config, config_key, value)

    return config


def _set_nested_value(config: Dict[str, Any], key: str, value: Any) -> None:
    """
    Set a nested value in a dictionary using dot notation.

    Args:
        config: Configuration dictionary
        key: Dot-separated key (e.g., "llm.openai_api_key")
        value: Value to set
    """
    keys = key.split(".")
    current = config

    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value


def merge_configs(file_config: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge file config and environment config with environment taking precedence.

    Args:
        file_config: Configuration from file
        env_config: Configuration from environment variables

    Returns:
        Merged configuration
    """
    merged = file_config.copy()

    def merge_nested(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                merge_nested(target[key], value)
            else:
                target[key] = value

    merge_nested(merged, env_config)
    return merged


def create_arxrec_config(config_dict: Dict[str, Any]) -> ArxrecConfig:
    """
    Create ArxrecConfig from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        ArxrecConfig object
    """
    # Extract arxrec-specific settings
    arxrec_settings = config_dict.get("arxrec", {})

    # Create ArxrecConfig
    arxrec_config = ArxrecConfig(
        user_profile=ResearcherProfile.from_config(config_dict),
        query=arxrec_settings.get("query", "cs.AI+cs.CV+cs.LG+cs.CL"),
        max_papers=arxrec_settings.get("max_papers", 50),
        send_empty=arxrec_settings.get("send_empty", False),
        ignore_patterns=arxrec_settings.get("ignore_patterns", []),
        debug=config_dict.get("debug", False),
    )

    return arxrec_config


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Build configuration
    env_config = build_config_from_envs()

    if args.config:
        file_config = load_config_from_file(args.config)
        # Merge with environment config (env takes precedence)
        config_dict = merge_configs(file_config, env_config)
    else:
        config_dict = env_config

    # Enable debug logging if specified
    if config_dict.get("debug", False):
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug(f"Final configuration: {config_dict}")

    # Create ArxrecConfig
    try:
        config = create_arxrec_config(config_dict)
    except Exception as e:
        logger.error(f"Failed to create ArxrecConfig: {e}")
        sys.exit(1)

    # Create and run agent
    agent = ArxrecAgent()

    try:
        logger.info("Starting Alithia research agent...")
        result = agent.run(config)

        if result["success"]:
            logger.info("✅ Research agent completed successfully")
            logger.info(f"📧 Email sent with {result['summary']['papers_scored']} papers")

            if result["errors"]:
                logger.warning(f"⚠️  {len(result['errors'])} warnings occurred")
                for error in result["errors"]:
                    logger.warning(f"   - {error}")
        else:
            logger.error("❌ Research agent failed")
            logger.error(f"Error: {result['error']}")

            if result["errors"]:
                logger.error("Additional errors:")
                for error in result["errors"]:
                    logger.error(f"   - {error}")

            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("🛑 Research agent interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
