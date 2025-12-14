# Copilot Instructions for csgocases-bot

These instructions guide AI coding agents working in this repository to be productive quickly. Focus on the current implementation patterns rather than aspirational practices.

## Architecture Overview

- **Domains:**
  - **`core/models`**: Data models and business actions.
    - `Post`: Normalized social post metadata.
    - `Promocode`: Extracts OCR code from an image, persists to Postgres, and automates claiming via Selenium.
  - **`integrations`**: External platform adapters. Example: `instagram.py` fetches profile and latest post via Instagram web API.
  - **`utils`**: Helpers (e.g., `driver.py` for saving/loading Selenium cookies).
  - **`core/app.py`**: Minimal Textual TUI example (`QuestionApp`). Not wired into flows yet.
  - **`src/main.py`**: Entry/demo script; currently showcases Instagram fetch.
- **Data Flow (Promocode):** `image_url -> requests -> PIL -> crop -> EasyOCR -> code -> psycopg2 -> DB` and `code -> Selenium (undetected-chromedriver) -> site claim -> toast status`.
- **Configuration:** See `src/config.py` (`DEBUG`, `URL`, `COOKIE_PATH`). `.env` is loaded in `Promocode` and expected to provide DB connection fields (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`).

## Developer Workflows

- **Run demo:**
  - `python -m src.main`
  - Adjust `src/main.py` to test `Promocode` or Instagram client.
- **Environment:** Python project (see `pyproject.toml`). Install system deps for OCR and browser automation if missing.
- **DB:** Ensure `.env` has Postgres credentials; `Promocode.store()` expects table `promocodes(code text, post_url text)` to exist.
- **OCR:** `easyocr.Reader(["en"], gpu=True)`; set GPU availability accordingly. If GPU is unavailable, change to `gpu=False` when needed.
- **Selenium:** Uses `undetected_chromedriver` with cookies from `data/cookies.pkl`. `load_cookies()` assumes a prior session; handle first-run gracefully.

## Conventions & Patterns

- **Dataclasses for models:** `Post`, `Promocode` encapsulate data with lazy-loaded properties (`image`, `code`).
- **Network operations:** Use `requests` directly; minimal retry/backoff. Keep timeouts explicit when adding new calls.
- **Instagram integration:** `InstagramAPI.fetch_profile()` supports a `DEBUG` mode that loads `data/mock_instagram_profile.json`. Follow this pattern for other integrations.
- **OCR preprocessing:** Images are cropped to the lower middle band: `(width*0.1, height*0.62, width*0.9, height*0.8)`, then converted to RGB, then passed to EasyOCR with `allowlist` for `A-Z0-9`.
- **Claim workflow:** Selenium locates wallet, switches to promocode tab, enters code, navigates a Cloudflare checkbox via shadow roots and simulated tab/space, then reads toast `status` and `message`.

## External Dependencies

- **Libraries:** `easyocr`, `psycopg2`, `requests`, `numpy`, `Pillow`, `python-dotenv`, `selenium`, `undetected-chromedriver`, `textual`.
- **Services:** Instagram web endpoints; target site (`URL` in config); Postgres database.

## Implementation Notes & Examples

- **Adding a new integration (e.g., X/Twitter):**
  - Create `src/integrations/x.py` with class similar to `InstagramAPI` that returns a `Post`.
  - Follow the `DEBUG` fixture approach for local development.
- **Using `Promocode`:**
  - Construct with `post_url` and `image_url`.
  - Read `promocode.code` (triggers OCR). Call `store()` to persist; call `claim()` to attempt redemption.
- **Cookies lifecycle:**
  - After successful manual login flow, call `utils.driver.save_cookies(driver)` to persist cookies to `COOKIE_PATH`.
  - Subsequent `claim()` calls depend on `load_cookies(driver)`.

## Testing & Debugging Tips

- **Mocked Instagram:** Set `DEBUG=True` in `src/config.py` and use `data/mock_instagram_profile.json` for consistent results.
- **OCR reliability:** If codes are misread, adjust crop region or add preprocessing (contrast, threshold) before EasyOCR.
- **Selenium flakiness:** Prefer explicit waits (`WebDriverWait`) and keep CSS selectors stable. Shadow DOM access is required for Cloudflare checkbox; avoid brittle assumptions.
- **Database errors:** Wrap operations; current code prints exceptions. For robust flows, surface errors to caller rather than `print`.

## File References

- Key files: `src/core/models/promocode.py`, `src/integrations/instagram.py`, `src/utils/driver.py`, `src/config.py`, `src/main.py`.

Keep instructions concise and practical. Update this doc when adding new integrations, changing claim flows, or adjusting OCR preprocessing.
