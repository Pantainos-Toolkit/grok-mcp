# grok-mcp

FastMCP server for searching X (Twitter) via the xAI Grok API.

Uses the xAI [Responses API](https://docs.x.ai/docs/api-reference) with the `x_search` server-side tool — Grok autonomously searches X, analyses results, and returns a grounded answer with citations.

## Tools

### `search_x`

Search X posts and get a summarised answer with source citations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | *required* | Natural-language search query |
| `allowed_handles` | `list[str]` | `None` | X usernames to restrict search to (max 10) |
| `excluded_handles` | `list[str]` | `None` | X usernames to exclude (max 10) |
| `from_date` | `str` | `None` | Start date filter (ISO 8601, e.g. `2026-02-01`) |
| `to_date` | `str` | `None` | End date filter (ISO 8601) |
| `enable_image_understanding` | `bool` | `True` | Analyse images in posts |
| `enable_video_understanding` | `bool` | `False` | Analyse video clips in posts |
| `model` | `str` | `grok-4-1-fast` | Grok model to use |
| `system_prompt` | `str` | `None` | Custom system prompt |
| `temperature` | `float` | `None` | Sampling temperature (0-2) |

**Returns:** `{ text, citations?, model, usage }`

## Setup

1. Get an API key from [console.x.ai](https://console.x.ai)

2. Copy the env template and add your key:
   ```bash
   cp .env.example .env
   # edit .env with your XAI_API_KEY
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Usage with Claude Code

Add to your Claude Code MCP config (`~/.claude/settings.json` or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "grok": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/grok", "python", "server.py"]
    }
  }
}
```

## Model Options

| Model | Context | Input $/1M | Output $/1M | Notes |
|-------|---------|-----------|------------|-------|
| `grok-4-1-fast` | 2M | $0.20 | $0.50 | Default — fast, cheap, great for search |
| `grok-4.1` | 256K | $3.00 | $15.00 | Flagship reasoning |
| `grok-3` | 128K | $2.00 | $10.00 | Stable general purpose |

Live search costs an additional ~$0.025 per source retrieved.
