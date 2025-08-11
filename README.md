# Alithia Researcher

A personal academic research agent that automatically discovers, analyzes, and recommends relevant papers from ArXiv based on your Zotero library and research interests.

## Features

- **Automated Paper Discovery**: Scans ArXiv for new papers in your research areas
- **Intelligent Filtering**: Uses your Zotero library to learn your preferences
- **Smart Summaries**: Generates TLDR summaries and extracts key information
- **Email Delivery**: Sends personalized paper recommendations via email
- **GitHub Actions Integration**: Automated daily runs with configurable schedules

## Quick Start

### AlithiaArxrec Agent

See [ALITHIA_ARXREC_AGENT.md](ALITHIA_ARXREC_AGENT.md)

### AlithiaLens Agent (oncoming)

See [ALITHIA_LENS_AGENT.md](ALITHIA_LENS_AGENT.md)

### AlithiaVigil Agent (oncoming)

See [ALITHIA_VIGIL_AGENT.md](ALITHIA_VIGIL_AGENT.md)

## Development

### Running Tests
```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

AGPL-3.0

## Thanks

The original agentic version is from [zotero-arxiv-daily](https://github.com/TideDra/zotero-arxiv-daily). Thanks [@TideDra](https://github.com/TideDra).
