# Project Overview

This project, `alithia-researcher`, is a personal academic research agent. It is designed to provide daily paper recommendations from ArXiv based on a user's research profile. The agent is built using Python and leverages the LangGraph framework to create a workflow for discovering, assessing, and delivering relevant academic papers.

The core technologies used in this project include:

*   **Python**: The primary programming language.
*   **Poetry**: For dependency management.
*   **LangGraph**: To structure the agent's workflow.
*   **ArXiv API**: To search for new academic papers.
*   **Zotero API**: To access the user's existing research library for context.
*   **scikit-learn & sentence-transformers**: For machine learning tasks, likely related to paper scoring and relevance assessment.
*   **OpenAI API**: For leveraging large language models, probably for summarization or content generation.
*   **Pinecone & Supabase**: For vector storage and database functionalities, respectively.

The agent's workflow is divided into the following main steps:

1.  **Profile Analysis**: The agent starts by analyzing the user's research profile to understand their interests.
2.  **Data Collection**: It then queries ArXiv for new papers and fetches the user's Zotero library for context.
3.  **Relevance Assessment**: The discovered papers are scored for relevance based on the user's profile.
4.  **Content Generation**: An email is crafted with the most relevant papers.
5.  **Communication**: The email is sent to the user.

# Building and Running

This project uses a `Makefile` that provides a convenient way to manage common tasks.

## Installation

To install the project dependencies, run:

```bash
make install
```

For development, you can install the development dependencies with:

```bash
make install-dev
```

## Running the Agent

The project defines three entry points in the `pyproject.toml` file: `arxrec`, `vigil`, and `lens`. To run the main agent, you can use the `arxrec` script:

```bash
poetry run arxrec
```

You will likely need to set up your environment variables in a `.env` file (based on `env.example`) to configure the agent with your API keys and preferences.

## Running Tests

To run the test suite, use the following command:

```bash
make test
```

You can also run unit and integration tests separately:

```bash
make test-unit
make test-integration
```

# Development Conventions

## Code Formatting

This project uses `black`, `isort`, and `autoflake` for code formatting. To format the code, run:

```bash
make format
```

To check if the code is properly formatted, run:

```bash
make format-check
```

## Linting

The project uses `flake8` for linting. To lint the code, run:

```bash
make lint
```

## Documentation

The documentation is built using Sphinx. To build the documentation, run:

```bash
make docs
```
