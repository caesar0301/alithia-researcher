# Alithia Researcher

A personal academic research agent that automatically discovers, analyzes, and recommends relevant papers from ArXiv based on your Zotero library and research interests.

## Features

- **Automated Paper Discovery**: Scans ArXiv for new papers in your research areas
- **Intelligent Filtering**: Uses your Zotero library to learn your preferences
- **Smart Summaries**: Generates TLDR summaries and extracts key information
- **Email Delivery**: Sends personalized paper recommendations via email
- **GitHub Actions Integration**: Automated daily runs with configurable schedules

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/alithia-researcher.git
   cd alithia-researcher
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Configure your environment**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

4. **Run the agent**
   ```bash
   poetry run python -m alithia.agents.arxrec
   ```

### GitHub Actions Setup

The repository includes automated workflows for daily paper recommendations:

#### 1. Daily Papers Workflow (`daily-papers.yml`)

**Schedule**: Runs daily at 23:00 UTC

**Setup**:
1. Go to your repository Settings → Secrets and variables → Actions
2. Add a new repository secret named `ARXREC_AGENT_CONFIG`
3. Set the value to your JSON configuration (see Configuration section below)

**Manual Trigger**: You can also manually trigger the workflow from the Actions tab.

#### 2. Test Workflow (`daily-papers-test.yml`)

**Purpose**: Testing the agent in debug mode with limited papers

**Setup**:
1. Add a repository secret named `ARXREC_AGENT_CONFIG_TEST`
2. Use a test configuration with debug mode enabled

**Trigger**: Manual trigger or on pull requests to main/develop branches

## Configuration

### Configuration Structure

The agent uses a JSON configuration like `arxrec_example.json`.

### Required Services

#### 1. Zotero
- **Purpose**: Source of your research preferences and existing papers
- **Setup**: 
  1. Create account at [zotero.org](https://www.zotero.org)
  2. Get your user ID from Settings → Feeds/API
  3. Generate API key from Settings → Keys

#### 2. OpenAI API
- **Purpose**: Generate TLDR summaries and extract paper information
- **Setup**: 
  1. Create account at [openai.com](https://openai.com)
  2. Generate API key from API Keys section

#### 3. Email Service (Gmail recommended)
- **Purpose**: Send paper recommendations
- **Setup**:
  1. Enable 2-factor authentication
  2. Generate App Password for the agent
  3. Use SMTP settings: `smtp.gmail.com:587`

### Configuration Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `zotero_id` | ✅ | Your Zotero user ID | `"1234567"` |
| `zotero_key` | ✅ | Your Zotero API key | `"abc123..."` |
| `smtp_server` | ✅ | SMTP server address | `"smtp.gmail.com"` |
| `smtp_port` | ✅ | SMTP server port | `587` |
| `sender` | ✅ | Sender email address | `"you@gmail.com"` |
| `sender_password` | ✅ | Email app password | `"app_password"` |
| `receiver` | ✅ | Recipient email address | `"recipient@example.com"` |
| `openai_api_key` | ✅ | OpenAI API key | `"sk-..."` |
| `research_interests` | ❌ | Your research areas | `["AI", "ML"]` |
| `max_paper_num` | ❌ | Max papers per email | `10` |
| `arxiv_query` | ❌ | ArXiv categories | `"cs.AI+cs.CV"` |
| `debug` | ❌ | Enable debug mode | `false` |

### GitHub Actions Configuration

#### For Production (`ARXREC_AGENT_CONFIG`)

1. **Create your configuration**:
   ```bash
   # Copy the example and customize
   cp arxrec_config.json my_config.json
   # Edit with your real values
   ```

2. **Convert to single line** (for GitHub Secrets):
   ```bash
   cat my_config.json | jq -c .
   ```

3. **Add to GitHub Secrets**:
   - Repository Settings → Secrets and variables → Actions
   - Add secret: `ARXREC_AGENT_CONFIG`
   - Value: The single-line JSON from step 2

#### For Testing (`ARXREC_AGENT_CONFIG_TEST`)

Create a test configuration with:
- `debug: true`
- `max_paper_num: 3`
- Test email addresses
- Limited ArXiv query

## Usage Examples

### Local Run with Config File
```bash
poetry run python -m alithia.agents.arxrec --config arxrec_config.json
```

### Local Run with Environment Variables
```bash
export ZOTERO_ID="your_id"
export ZOTERO_KEY="your_key"
# ... set other variables
poetry run python -m alithia.agents.arxrec
```

### Manual GitHub Actions Trigger
1. Go to Actions tab
2. Select "Daily Papers - ArXiv Research Agent"
3. Click "Run workflow"
4. Choose branch and run

## Development

### Running Tests
```bash
# All tests
poetry run pytest

# Unit tests only
poetry run pytest tests/unit/

# Integration tests only
poetry run pytest tests/integration/
```

### Project Structure
```
alithia/
├── agents/
│   └── arxrec/          # ArXiv recommendation agent
├── core/                # Core functionality
│   ├── arxiv_client.py  # ArXiv API client
│   ├── zotero_client.py # Zotero API client
│   ├── email_utils.py   # Email functionality
│   └── profile.py       # Configuration models
└── tests/               # Test suite
```

## Troubleshooting

### Common Issues

1. **"Zotero API key invalid"**
   - Regenerate your Zotero API key
   - Check user ID is correct

2. **"SMTP authentication failed"**
   - Use App Password, not regular password
   - Enable 2FA on Gmail account

3. **"OpenAI API key invalid"**
   - Check API key format starts with `sk-`
   - Verify account has credits

4. **"No papers found"**
   - Check ArXiv query format
   - Verify Zotero library has papers
   - Try broader categories

### Debug Mode

Enable debug mode to see detailed logs:
```json
{
  "debug": true,
  "max_paper_num": 3
}
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