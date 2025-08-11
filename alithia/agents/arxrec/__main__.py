"""
Main entry point for the Alithia research agent.
Replicates zotero-arxiv-daily functionality using agentic architecture.
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from alithia.agents.arxrec.arxrec_agent import ArxrecAgent

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


def build_config_from_envs() -> dict:
    """
    Build configuration dictionary from environment variables.

    Returns:
        Configuration dictionary
    """
    config = {}

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
        "openai_api_key": "OPENAI_API_KEY",
        "openai_api_base": "OPENAI_API_BASE",
        "model_name": "MODEL_NAME",
        "language": "LANGUAGE",
        "debug": "DEBUG",
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
                elif config_key in ["send_empty", "debug"]:
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
    required_fields = [
        "zotero_id",
        "zotero_key",
        "smtp_server",
        "smtp_port",
        "sender",
        "receiver",
        "sender_password",
        "openai_api_key",
    ]

    missing = [field for field in required_fields if field not in config or not config[field]]

    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        return False

    return True


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Build configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = build_config_from_envs()

    if config.get("debug", False):
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug(f"Final configuration: {config}")

    # Validate configuration
    if not validate_config(config):
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
