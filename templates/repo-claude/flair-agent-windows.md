# CLAUDE.md — flair-agent-windows

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Go 1.24+, Windows ETW (Event Tracing for Windows), Npcap  
**Role**: Windows capture agent — ETW network events + Npcap packet capture → `Flow` structs → flair-core  
**OS required**: Windows 11 23H2+ / Windows Server 2022+  
**Privilege required**: `SeSecurityPrivilege` or Administrator  
**Licence**: BSL-1.1

---

## Build & test commands

```bash
# Build (Windows target — cross-compile from Linux possible)
GOOS=windows GOARCH=amd64 go build -tags windows ./...

# Unit tests (Linux CI — Windows-specific code gated behind build tags)
go test ./...

# Windows-only integration tests (requires Windows runner in CI)
go test -tags windows,integration ./...

# Linter
golangci-lint run --build-tags windows ./...
```

---

## Repo structure

```
flair-agent-windows/
  cmd/flair-agent-windows/  ← entrypoint, Windows service bootstrap
  internal/
    etw/                    ← ETW session management, event consumer
    npcap/                  ← Npcap packet capture (WinPcap API)
    protocol/               ← DPI (shared logic with flair-agent where possible)
    ingest/                 ← batch sender to flair-core (same as flair-agent)
    service/                ← Windows service lifecycle (start/stop/pause)
    config/
  api/                      ← agent HTTP endpoints (/healthz, /readyz, /metrics)
```

---

## Key differences from flair-agent (Linux)

| Aspect | flair-agent (Linux) | flair-agent-windows |
|---|---|---|
| Capture | eBPF (tc hook) | ETW + Npcap |
| Privilege | CAP_BPF | SeSecurityPrivilege / Admin |
| Service | systemd | Windows Service |
| Build tags | `//go:build linux` | `//go:build windows` |

Both produce the same `Flow` struct — same contract, different capture path.

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-solid-go | all US |
| 1 (always) | skill-error-handling | all US |
| 1 (always) | skill-ac-traceability | all US |
| 1 (always) | skill-observability | all US |
| 2 | skill-authentication | enrollment / mTLS changes |
| 2 | skill-performance | throughput / latency US |

---

## Repo-specific rules

- All Windows API calls wrapped in `internal/etw` or `internal/npcap` — no raw `syscall.NewProc` in business logic
- Build tags `//go:build windows` on every file that uses Windows-specific imports
- Npcap DLL path must be configurable — never hardcoded
- ETW session name format: `FLAIR-{hostname}-{pid}` — prevents session name collision
