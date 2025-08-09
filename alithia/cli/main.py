"""
Main entry point for the Alithia research agent.
Replicates zotero-arxiv-daily functionality using agentic architecture.
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from alithia.agents.arxrec.research_agent import ResearchAgent

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
        description="Alithia Research Agent - Daily ArXiv paper recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with environment variables
  python -m alithia.main
  
  # Run with command line arguments
  python -m alithia.main --zotero-id 12345678 --zotero-key abc123 --debug
  
  # Run with configuration file
  python -m alithia.main --config config.json
        """,
    )

    # Required arguments
    parser.add_argument("--zotero-id", type=str, help="Zotero user ID")
    parser.add_argument("--zotero-key", type=str, help="Zotero API key")
    parser.add_argument("--smtp-server", type=str, help="SMTP server")
    parser.add_argument("--smtp-port", type=int, help="SMTP port")
    parser.add_argument("--sender", type=str, help="Sender email address")
    parser.add_argument("--receiver", type=str, help="Receiver email address")
    parser.add_argument("--sender-password", type=str, help="Sender email password")

    # Optional arguments
    parser.add_argument("--zotero-ignore", type=str, help="Zotero collections to ignore (gitignore-style patterns)")
    parser.add_argument("--send-empty", action="store_true", help="Send email even if no papers found")
    parser.add_argument("--max-paper-num", type=int, default=50, help="Maximum number of papers to recommend")
    parser.add_argument("--arxiv-query", type=str, default="cs.AI+cs.CV+cs.LG+cs.CL", help="ArXiv search query")
    parser.add_argument("--use-llm-api", action="store_true", help="Use OpenAI API for TLDR generation")
    parser.add_argument("--openai-api-key", type=str, help="OpenAI API key")
    parser.add_argument("--openai-api-base", type=str, default="https://api.openai.com/v1", help="OpenAI API base URL")
    parser.add_argument("--model-name", type=str, default="gpt-4o", help="LLM model name")
    parser.add_argument("--language", type=str, default="English", help="Language for TLDR summaries")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", type=str, help="Configuration file path (JSON)")

    return parser


def load_config_from_file(config_path: str) -> dict:
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


def build_config_from_args(args) -> dict:
    """
    Build configuration dictionary from arguments.

    Args:
        args: Parsed arguments

    Returns:
        Configuration dictionary
    """
    config = {}

    # Map argument names to config keys
    arg_mapping = {
        "zotero_id": "ZOTERO_ID",
        "zotero_key": "ZOTERO_KEY",
        "smtp_server": "SMTP_SERVER",
        "smtp_port": "SMTP_PORT",
        "sender": "SENDER",
        "receiver": "RECEIVER",
        "sender_password": "SENDER_PASSWORD",
        "zotero_ignore": "ZOTERO_IGNORE",
        "send_empty": "SEND_EMPTY",
        "max_paper_num": "MAX_PAPER_NUM",
        "arxiv_query": "ARXIV_QUERY",
        "use_llm_api": "USE_LLM_API",
        "openai_api_key": "OPENAI_API_KEY",
        "openai_api_base": "OPENAI_API_BASE",
        "model_name": "MODEL_NAME",
        "language": "LANGUAGE",
        "debug": "DEBUG",
    }

    # Add command line arguments
    for arg_name, config_key in arg_mapping.items():
        value = getattr(args, arg_name.replace("-", "_"))
        if value is not None:
            config[config_key.lower()] = value

    # Add environment variables (lower priority than command line)
    env_mapping = {
        "zotero_id": "ZOTERO_ID",
        "zotero_key": "ZOTERO_KEY",
        "smtp_server": "SMTP_SERVER",
        "smtp_port": "SMTP_PORT",
        "sender": "SENDER",
        "receiver": "RECEIVER",
        "sender_password": "SENDER_PASSWORD",
        "zotero_ignore": "ZOTERO_IGNORE",
        "send_empty": "SEND_EMPTY",
        "max_paper_num": "MAX_PAPER_NUM",
        "arxiv_query": "ARXIV_QUERY",
        "use_llm_api": "USE_LLM_API",
        "openai_api_key": "OPENAI_API_KEY",
        "openai_api_base": "OPENAI_API_BASE",
        "model_name": "MODEL_NAME",
        "language": "LANGUAGE",
    }

    for config_key, env_key in env_mapping.items():
        if config_key not in config:
            value = get_env(env_key)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ["smtp_port", "max_paper_num"]:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif config_key in ["send_empty", "use_llm_api"]:
                    value = str(value).lower() in ["true", "1", "yes"]
                config[config_key] = value

    return config


def validate_config(config: dict) -> bool:
    """
    Validate configuration has all required fields.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["zotero_id", "zotero_key", "smtp_server", "smtp_port", "sender", "receiver", "sender_password"]

    missing = [field for field in required_fields if field not in config or not config[field]]

    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        return False

    # Validate LLM API requirements
    if config.get("use_llm_api", False) and not config.get("openai_api_key"):
        logger.error("OpenAI API key required when USE_LLM_API=True")
        return False

    return True


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Configure logging based on debug mode
    if args.debug or get_env("DEBUG", "").lower() in ["true", "1", "yes"]:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Build configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = build_config_from_args(args)

    # Validate configuration
    if not validate_config(config):
        sys.exit(1)

    # Create and run agent
    agent = ResearchAgent()

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
