# IFLOW.md

This file provides guidance to iFlow Cli when working with code in this repository.

## Development Commands

### Setup
- `make setup` - Install all dependencies (including dev dependencies)
- `make install` - Install production dependencies only
- `make install-dev` - Install development dependencies

### Testing
- `make test` - Run all tests
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests only
- `make test-coverage` - Run tests with coverage report
- `make test-watch` - Run tests in watch mode

### Code Quality
- `make format` - Format code with black, isort, and autoflake
- `make format-check` - Check if code is properly formatted
- `make lint` - Lint code with flake8
- `make lint-fix` - Auto-fix linting issues where possible
- `make quality` - Run all quality checks (formatting + linting)
- `make autofix` - Auto-fix all code quality issues

### Build and Release
- `make build` - Build package
- `make build-wheel` - Build wheel distribution
- `make build-sdist` - Build source distribution
- `make package` - Clean and build for distribution
- `make publish` - Publish package to PyPI
- `make publish-test` - Publish package to TestPyPI

### Documentation
- `make docs` - Build documentation
- `make docs-serve` - Serve documentation locally

### Utilities
- `make clean` - Clean Python cache and build artifacts
- `make shell` - Activate development shell
- `make requirements` - Generate requirements files

## Codebase Architecture

### Overview
Alithia is a multi-agent research assistant with three specialized agents:
1. **AlithiaVigil** - Proactive topic monitoring agent
2. **AlithiaArxrec** - Personalized ArXiv recommendation agent
3. **AlithiaLens** - Deep paper interaction agent

All agents share a common core infrastructure that includes:
- Configuration management
- Vector store (Pinecone)
- Table store (Supabase)
- PDF processing (MinerU)
- Embedding and reranking (sentence-transformers)
- LLM integration (OpenAI via cogents)

### Core Components
Located in `alithia/core/`:
- `agent_state.py` - Centralized state management for LangGraph workflows
- `paper.py` - Data models for papers (ArxivPaper, ScoredPaper, EmailContent)
- `profile.py` - User research profile and configuration
- `arxiv_client.py` - ArXiv paper discovery
- `zotero_client.py` - Zotero library integration
- `vector_store.py` - Pinecone vector database wrapper
- `table_store.py` - Supabase table storage wrapper
- `pdf_processor.py` - PDF parsing with MinerU
- `embedding.py` - Text embedding and reranking with sentence-transformers
- `llm_utils.py` - LLM integration via cogents
- `email_utils.py` - Email content generation and delivery

### Agent Structure
Each agent follows a consistent structure:
- `__main__.py` - CLI entrypoint using Typer
- `agent.py` - LangGraph workflow orchestrator
- `nodes.py` - Workflow nodes implementing specific functionality
- Agent-specific modules (e.g., `recommender.py` for Arxrec)

Agents use LangGraph for workflow orchestration, with each agent implementing a specialized research workflow.

### Key Technologies
- **Orchestration**: LangGraph for agent workflows
- **Vector DB**: Pinecone for embeddings storage
- **Relational DB**: Supabase for metadata storage
- **PDF Processing**: MinerU for parsing and segmentation
- **Embeddings**: sentence-transformers for text embeddings and reranking
- **LLM**: OpenAI API (configurable via cogents)
- **CLI**: Typer for command-line interfaces