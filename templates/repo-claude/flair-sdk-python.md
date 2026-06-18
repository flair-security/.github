# CLAUDE.md — flair-sdk-python

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Python 3.12+, httpx 0.28+, pydantic v2  
**Role**: Official Python client SDK for the flair-core REST API  
**Licence**: Apache-2.0

---

## Build & test commands

```bash
# Install
pip install -e ".[dev]"

# Unit tests
pytest tests/unit/

# Integration tests (requires flair-core)
FLAIR_CORE_URL=http://localhost:8080 pytest tests/integration/ -m integration

# Linter + type check
ruff check .
mypy flair_sdk/

# Generate from OpenAPI
openapi-python-client generate --path openapi/flair-core-v1.yaml --config openapi-config.yaml

# Build package
python -m build
```

---

## Repo structure

```
flair-sdk-python/
  flair_sdk/            ← main package
    client.py           ← FlairClient class
    models/             ← Pydantic v2 models (generated + hand-written)
    exceptions.py       ← FlairAPIError hierarchy
    pagination.py       ← PageIterator
    auth.py             ← BearerToken, OAuth2ClientCredentials
  tests/
    unit/
    integration/
  examples/             ← runnable scripts
  openapi/              ← OpenAPI spec copy
  pyproject.toml
```

---

## SDK design rules

```python
from flair_sdk import FlairClient

client = FlairClient(
    base_url="https://flair.example.com",
    token="...",         # or oauth2_credentials=(client_id, secret)
    timeout=30.0,
    retries=3,
)

# Async support
async with FlairClient(...) as client:
    async for alert in client.alerts.list(status="open"):
        print(alert.id)
```

- Sync and async client via `httpx` (same code path)
- Full type hints — mypy strict mode, no `Any`
- Pydantic v2 models for all API types
- Custom exception hierarchy: `FlairAPIError → FlairAuthError / FlairNotFoundError / FlairRateLimitError`

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-api-design | all US |
| 1 (always) | skill-ac-traceability | all US |
| 2 | skill-authentication | auth / token changes |

---

## Repo-specific rules

- No `requests` library — `httpx` only (async support requirement)
- Published to PyPI under `flair-sdk` — bump version in `pyproject.toml` on every release
- Never import flair-core internals — SDK depends on OpenAPI contract only
- All models have `.model_dump()` and `.model_validate()` (Pydantic v2)
