# CSGOCases Bot - Copilot Instructions

## Project Overview

A Python bot that scrapes promocodes from CSGOCases social media accounts (X/Twitter, Instagram, Facebook, Discord) and auto-redeems them on the CSGOCases website. Uses a Textual TUI for interaction.

## Architecture

```
src/
├── main.py              # Entry point - launches TUI app
├── config.py            # Static config (usernames, API tokens, DEBUG flag)
├── integrations/        # Platform-specific API clients
├── models/post.py       # Unified Post dataclass for all platforms
├── repositories/        # PostgreSQL persistence (psycopg2)
├── tui/app.py           # Textual terminal UI
└── utils/               # OCR (easyocr) and HTML parsing helpers
```

**Data Flow**: Integration fetches Post → OCR extracts promocode from image → Repository checks/stores → CSGOCasesAPI claims via Selenium

## Key Patterns

### Integration API Classes

All integrations follow the same pattern in `src/integrations/`:

- Class with `fetch_latest_post(username: str) -> Optional[Post]` method
- Returns unified `Post` dataclass from `models/post.py`
- Use `DEBUG` flag from `config.py` to load mock JSON from `data/` instead of real API calls

```python
if DEBUG:  # Mock response pattern used everywhere
    with open("data/mock_*.json", "r", encoding="utf-8") as f:
        response = json.load(f)
```

### CSGOCases Website Automation

`CSGOCasesAPI` uses context manager pattern with `undetected_chromedriver`:

```python
with CSGOCasesAPI() as api:
    api.claim_promocode("CODE123")
```

Handles Cloudflare challenges via shadow DOM traversal and ActionChains.

### Environment Variables

Loaded via `python-dotenv`. Required in `.env`:

- `DISCORD_AUTH_TOKEN`, `X_AUTH_TOKEN`, `X_CSRF_TOKEN` - API auth
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` - PostgreSQL

## Development

### Running

```bash
cd src && python main.py  # Launches TUI
```

### Debug Mode

Set `DEBUG = True` in `config.py` to use mock JSON files in `data/` instead of live API calls. Mock files mirror real API response structures.

### Dependencies

- `textual` - Terminal UI framework
- `undetected_chromedriver` - Selenium wrapper for anti-bot bypass
- `easyocr` - Extract promocode text from images (GPU-enabled)
- `psycopg2` - PostgreSQL driver
- `bs4` - HTML parsing for Facebook scraping

### Adding New Integrations

1. Create `src/integrations/newplatform.py` with class implementing `fetch_latest_post()`
2. Return `Post` dataclass with platform-specific data mapped to common fields
3. Add mock JSON in `data/mock_newplatform.json` for DEBUG mode
4. Export in `src/integrations/__init__.py`

## Code Conventions

- Type hints on all function signatures
- `Optional[T]` return types for methods that may fail
- Docstrings with triple quotes for public methods
- Raw API responses stored in `Post.raw_data` for debugging
- Use `deep_find()` from `utils/soup.py` for nested JSON traversal
