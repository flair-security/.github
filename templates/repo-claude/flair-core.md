# CLAUDE.md — flair-core

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Go 1.24+, PostgreSQL 17, Redis 8, gRPC  
**Role**: Central server — ingest flows, store graph, score paths, expose REST+gRPC API  
**Licence**: BSL-1.1

---

## Build & test commands

```bash
# Build
go build ./...

# Unit tests
go test ./...

# Integration tests (requires Docker for PostgreSQL + Redis)
go test -tags integration ./...

# Run full stack locally (PostgreSQL 17 + Redis 8)
docker compose -f docker-compose.dev.yml up

# Database migrations (goose)
goose -dir migrations postgres "$DATABASE_URL" up
goose -dir migrations postgres "$DATABASE_URL" status

# Linter
golangci-lint run ./...

# Generate mocks (mockgen)
go generate ./...

# gRPC code generation
buf generate
```

---

## Repo structure

```
flair-core/
  cmd/flair-core/       ← entrypoint, server bootstrap
  internal/
    api/                ← REST handlers (chi router)
    auth/               ← OIDC middleware, mTLS verifier, RBAC
    graph/              ← GraphStore implementation (PostgreSQL)
    scoring/            ← ScoringStrategy implementations, CompositeScorer
    ingest/             ← IngestQueue consumer, Flow validation, batch insert
    notification/       ← alert dispatcher
    config/             ← YAML config struct
  migrations/           ← goose SQL migrations (numbered)
  proto/                ← .proto definitions (flair/v1/)
  api/openapi/          ← OpenAPI 3.1 spec (generated)
  e2e/                  ← Playwright specs for REST API flows
```

---

## Key interfaces owned by this repo

```go
type GraphStore interface {
    UpsertFlow(ctx context.Context, f *flair.Flow) error
    QueryPaths(ctx context.Context, q PathQuery) ([]Path, error)
    GetAssetGraph(ctx context.Context, assetID string) (*Graph, error)
}

type AuthProvider interface {
    ValidateToken(ctx context.Context, token string) (*Claims, error)
    ValidateClientCert(ctx context.Context, cert *x509.Certificate) (*AgentClaims, error)
}

type IngestQueue interface {
    Enqueue(ctx context.Context, flow *flair.Flow) error
    BatchDequeue(ctx context.Context, size int) ([]*flair.Flow, error)
}

type ScoringEngine interface {
    Score(ctx context.Context, path []flair.Flow) (ScoreResult, error)
}
```

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-solid-go | all US |
| 1 (always) | skill-go-service-layer | all US |
| 1 (always) | skill-error-handling | all US |
| 1 (always) | skill-ac-traceability | all US |
| 1 (always) | skill-bdd-architecture | all US |
| 1 (always) | skill-observability | all US |
| 2 | skill-api-design | REST/gRPC endpoint changes |
| 2 | skill-authentication | auth/RBAC changes |
| 2 | skill-security-scoring | scoring logic changes |
| 2 | skill-testing-strategy | test infrastructure |
| 3 | skill-devops-cicd | CI / Docker / migrations |

---

## Repo-specific rules

- Migrations are append-only — no editing existing migration files
- Never access DB directly from a handler — always go through a repository/store interface
- Redis is cache-only — no business logic state in Redis; all state is canonical in PostgreSQL
- gRPC services auto-generate OpenAPI via `buf generate` — do not manually edit `api/openapi/`
- Cursor-based pagination only — offset pagination blocked (see skill-api-design)
