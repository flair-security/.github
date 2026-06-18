# CLAUDE.md — flair-sdk-go

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Go 1.24+, zero external runtime dependencies  
**Role**: Official Go client SDK for the flair-core REST+gRPC API  
**Licence**: Apache-2.0

---

## Build & test commands

```bash
# Build
go build ./...

# Unit tests (no external deps)
go test ./...

# Integration tests (requires flair-core running)
FLAIR_CORE_URL=http://localhost:8080 go test -tags integration ./...

# Linter
golangci-lint run ./...

# Generate from OpenAPI
oapi-codegen -config oapi-codegen.yaml openapi/flair-core-v1.yaml

# Examples
go run examples/list-alerts/main.go
```

---

## Repo structure

```
flair-sdk-go/
  flair/                ← main package — Client, options, types
  flair/v1/             ← generated types from OpenAPI
  internal/             ← HTTP transport, retry, auth
  examples/             ← runnable usage examples
  openapi/              ← OpenAPI spec copy (synced from flair-core)
  oapi-codegen.yaml     ← code generation config
```

---

## SDK design rules

- Zero mandatory dependencies — only stdlib for core functionality
- `Client` struct with functional options pattern:
  ```go
  c, err := flair.NewClient(baseURL,
      flair.WithBearerToken(token),
      flair.WithTimeout(30*time.Second),
      flair.WithRetry(3),
  )
  ```
- All methods return `(result, error)` — no panics
- Context-first on every method: `func (c *Client) ListAlerts(ctx context.Context, ...) `
- Pagination via iterator: `c.Alerts().List(ctx, filter)` returns `*PageIterator[Alert]`

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-solid-go | all US |
| 1 (always) | skill-error-handling | all US |
| 1 (always) | skill-api-design | all US |
| 1 (always) | skill-ac-traceability | all US |
| 2 | skill-authentication | auth / token changes |

---

## Repo-specific rules

- Never import `flair-core` internal packages — SDK depends only on OpenAPI contract
- Semantic versioning: v0.x.0 until stable API, then v1.x.0
- Breaking changes require major version bump and migration guide in CHANGELOG.md
- All public types serialisable to/from JSON
- Examples must compile and run against a live flair-core instance
