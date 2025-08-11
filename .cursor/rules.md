### Alithia Engineering Rules (Global Constraints)

- **PRD compliance**: All designs and implementations must align with `specs/prd.md`.
- **Language**: Python only.
- **Orchestration**: Use LangGraph for agent workflows.
- **CLI**: Use Typer for CLI entrypoints.

### Agents and Scope

- **Agents**: `vigil`, `arxrec`, `lens` live under `alithia/agents/<agent_name>`.
- **Core**: Shared modules must reside under `alithia/core` and be reused by all agents.
- **Scope control**: Do not implement features outside the targeted agent unless explicitly requested. Avoid adding unrelated modules, services, or tests when not requested.

### PDF Processing

- **Library**: Use MinerU for PDF parsing/segmentation.
- **Abstraction**: Provide a wrapper in `alithia/core/pdf_processor.py` that returns structured text chunks (id, text, page, offset). Encapsulate import differences across MinerU versions.
- **Input**: Support local PDF paths at minimum; optional fetchers (arXiv/DOI/title) can be layered on top.

### Embeddings and Reranking

- **Embeddings**: Use `sentence-transformers` for all text embeddings.
- **Reranking**: Use `sentence-transformers` CrossEncoder-based rerankers for query-aware ranking.
- **Defaults**:
  - Embedding model default: `mixedbread-ai/mxbai-embed-large-v1` (configurable).
  - Reranker default: `cross-encoder/ms-marco-MiniLM-L-6-v2` (configurable).
- **Normalization**: Normalize embeddings to unit length before vector upsert and similarity search.

### Storage and Persistence

- **Vector storage**: Use Pinecone exclusively for vector similarity search.
  - Environment: `PINECONE_API_KEY` (required), `PINECONE_INDEX`, `PINECONE_NAMESPACE`.
  - Implement a reusable client in `alithia/core/vector_store.py` with upsert/query helpers.
- **Table storage**: Use Supabase exclusively for relational/metadata tables.
  - Environment: `SUPABASE_URL` (required), `SUPABASE_ANON_KEY` (required).
  - Provide helpers in `alithia/core/table_store.py` for document/chunk metadata CRUD.
- **No alternate stores**: Do not introduce other DBs/vector stores unless explicitly approved.

### LLMs and Tooling

- **LLM client**: Use `cogents.common.llm.get_llm_client` via a helper in `alithia/core/llm_utils.py`.
- **Provider**: Default to OpenAI provider; model configurable via profile/config.
- **Usage**: Generate answers/summaries using `llm.generate(messages=[...])` with system/user roles.
- **Tools**: Do not implement a custom tool base class. All tools must subclass `langchain_core.tools.BaseTool` and declare a `args_schema` pydantic model for inputs. Optional `execute()` helpers are allowed for internal usage.

### Configuration and Environment

- **Environment file**: Keep `env.example` authoritative for required variables.
- **New env vars (used across agents)**:
  - Pinecone: `PINECONE_API_KEY`, `PINECONE_INDEX`, `PINECONE_NAMESPACE` (optional)
  - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DOC_TABLE` (default `lens_documents`), `SUPABASE_CHUNK_TABLE` (default `lens_chunks`)
- **Profiles**: Reuse `alithia/core/profile.py` as the primary configuration model. Extend cautiously and keep backward compatible keys.

### Code Structure and Style

- **Directory layout**: Follow structure in `specs/prd.md`.
- **Common modules**: Place shared utilities in `alithia/core` and reuse across agents (PDF parsing, embeddings, vector/table stores, LLM utils).
- **Imports**: Agents should import from `alithia/core/*` for shared logic.
- **Code style**: Follow the repository’s formatting and typing discipline (pydantic models, explicit types for public APIs, early returns, minimal nesting).
- **Data models**: Implement data models based on pydantic library instead of dataclasses.

### Testing and Ops

- **Tests**: Do not add or run tests unless explicitly requested. Place unittests under folder `tests/unit` and integration under `tests/integration`.
- **Runtime**: Assume non-interactive execution for internal steps; CLI must be user-friendly.
- **Run tests**: `make test-unit` for unit tests. `make test-integration` for integration tests which are marked by `pytest.mark.integration`.

### Compatibility and Backwards Safety

- **Non-breaking edits**: Maintain compatibility with existing CLI commands and public method signatures unless the change is explicitly approved.
- **Resilience**: Handle missing/invalid configs with clear errors; avoid silent failures.
- **Performance**: Batch embeddings and vector upserts where possible; avoid excessive network round-trips.