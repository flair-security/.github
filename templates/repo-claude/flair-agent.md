# CLAUDE.md — flair-agent

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`
> (assumes repos cloned side by side under same parent directory)

---

## Quick reference

**Stack**: Go 1.24+, C, eBPF (libbpf), Linux kernel ≥ 5.15  
**Role**: Network capture agent — produces `Flow` structs, sends to flair-core ingest API  
**CAP required**: `CAP_NET_ADMIN`, `CAP_BPF` (or `CAP_SYS_ADMIN` on older kernels)  
**Licence**: BSL-1.1

---

## Build & test commands

```bash
# Build (Linux only — eBPF programs require Linux)
go build ./...

# Unit tests (no kernel required)
go test ./...

# Integration tests (requires Docker + Linux kernel ≥ 5.10)
go test -tags integration ./...

# eBPF compilation (requires clang + libbpf-dev)
make ebpf

# Full local stack (agent + core + UI)
docker compose -f docker-compose.dev.yml up

# Linter
golangci-lint run ./...

# BPF object inspection
sudo bpftool prog list
sudo bpftool map list
```

---

## Repo structure

```
flair-agent/
  cmd/flair-agent/        ← entrypoint, CLI flags, config loading
  internal/
    collector/            ← eBPF map reader, perf buffer consumer
    protocol/             ← DPI, protocol detection (HTTP/gRPC/DNS/TLS)
    tls/                  ← JA3/JA3S fingerprinting
    ingest/               ← batch builder, HTTP sender to flair-core
    config/               ← YAML config struct
  ebpf/                   ← C eBPF programs (tc, kprobe, uprobe)
  api/                    ← agent HTTP endpoints (/healthz, /readyz, /metrics)
  testdata/               ← pcap fixtures for protocol tests
  e2e/                    ← Playwright specs (not applicable — Go binary)
```

---

## Key interfaces owned by this repo

**Produces** (sends to flair-core):
```go
// Flow struct — see CLAUDE.md for the full 17-field definition
// This is the single contract shared across all repos
type Flow struct { ... }
```

**Exposes** (HTTP endpoints on agent):
```
GET /healthz         → 200 OK or 503
GET /readyz          → 200 OK when eBPF programs attached
GET /metrics         → Prometheus text format
POST /config/reload  → hot reload (mTLS required)
```

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-solid-go | all US |
| 1 (always) | skill-error-handling | all US |
| 1 (always) | skill-ac-traceability | all US |
| 1 (always) | skill-observability | all US |
| 1 (always) | skill-ebpf-architecture | repo = flair-agent |
| 2 (conditional) | skill-authentication | AC mentions mTLS / enrollment / token |
| 2 (conditional) | skill-performance | AC mentions throughput / latency / memory |
| 2 (conditional) | skill-devops-cicd | CI changes / Dockerfile |

---

## Repo-specific rules

- All eBPF programs must have a fallback path when not running as root (graceful degradation, not panic)
- Binary size limit: 20MB (checked in CI via Gate 3)
- No CGO outside `internal/ebpf/` — cgo breaks cross-compilation toolchain
- eBPF maps use pinning under `/sys/fs/bpf/flair-agent/` — document map names in code
- Kernel version compatibility must be documented per eBPF feature in the relevant GoDoc
