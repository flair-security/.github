# FLAIR Architecture

> Central architecture reference for the flair-sec organisation.
> This document is the source of truth for cross-repo decisions.
> Changes to this document require an ADR in `docs/ADR/`.
>
> This content now also lives in the flair-docs Docusaurus site under docs/architecture/ — that copy is the one intended for public browsing; this file remains the source of truth for now.

---

## Overview

FLAIR is a self-hosted, single-tenant application flow mapping platform.
It captures network flows at the OS level, enriches them with protocol and TLS metadata,
stores them in a graph database, and exposes a scoring and alerting interface for security teams.

```text
┌─────────────────────────────────────────────────────────────┐
│                    Organisation network                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ flair-agent  │  │ flair-agent  │  │  flair-agent-k8s │  │
│  │ (Linux eBPF) │  │  (Windows)   │  │  (K8s sidecar)   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                   │             │
│         └─────────────────┼───────────────────┘             │
│                           │ mTLS (TLS 1.3)                  │
│                    ┌──────▼───────┐                         │
│                    │  flair-core  │                         │
│                    │  (REST API)  │                         │
│                    │  (GraphDB)   │                         │
│                    └──────┬───────┘                         │
│                           │                                 │
│                    ┌──────▼───────┐                         │
│                    │   flair-ui   │                         │
│                    │  (Angular)   │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### flair-agent (Linux eBPF)

Captures network flows at the kernel level using eBPF TC hooks.
Runs as a non-root process with `CAP_NET_ADMIN` and `CAP_SYS_PTRACE` only.
Performs first-packet DPI (512 bytes) for protocol detection.
Computes JA3 fingerprint in userspace from TLS ClientHello bytes.
Batches flows (1000 flows or 10 seconds) and sends to flair-core via mTLS.
Buffers locally (up to 100MB on disk) when flair-core is unreachable.

### flair-core

Central server. Receives flows from agents, scores them, stores them in PostgreSQL + AGE,
and exposes a REST API authenticated via OIDC (users) and mTLS (agents).
Single instance per organisation — no multi-tenancy.

### flair-ui

Angular SPA served by nginx. Connects to flair-core REST API.
Renders the interactive flow map using D3.js force-directed graph.
Primary user: RSSI / security auditor.

---

## Flow Contract

The `Flow` struct is the central cross-repo interface. Any change is a breaking change requiring an ADR, coordinated PRs, and the `flow-contract` label on all PRs.

**Update order on any change**: `flair-agent` → `flair-core` → `flair-ui`

```go
type Flow struct {
    // Identity
    AgentID    string            // unique identifier of the emitting agent

    // Network
    SrcIP      string
    SrcPort    int
    DstIP      string
    DstPort    int
    Direction  string            // "outbound" | "inbound" | "internal"

    // Application protocol
    Protocol   string            // "HTTP/1.1" | "gRPC" | "SQL" | "AMQP" | "Redis"...

    // Encryption
    TLSVersion     string        // "TLS1.3" | "TLS1.2" | "" (none)
    TLSCipherSuite string        // e.g. "TLS_AES_256_GCM_SHA384" — empty if unencrypted
    JA3Hash        string        // TLS client fingerprint — empty if unencrypted
    Encrypted      bool

    // Source process
    SrcProcess  string
    SrcPID      int
    ContainerID string            // optional — enriched by flair-agent-k8s

    // Metrics
    BytesTransferred int64

    // Time
    Timestamp  time.Time

    // Extensible metadata
    Metadata   map[string]string  // "environment" | "owner" | "app_id"
                                   // "criticality" | "zone" | ...
}
```

Optional fields (`ContainerID`, `JA3Hash`, `TLSCipherSuite`): zero value is acceptable, never block a minimal agent implementation.
`Metadata` is intentionally open — do not add dedicated columns for concepts that belong here.

Breaking changes to the Flow contract require:

1. An ADR in `docs/ADR/`
2. Coordinated PRs across all affected repos opened simultaneously
3. Label `flow-contract` on all PRs

---

## Abstract Interfaces

These interfaces allow swapping implementations without changing callers.
Implementations live in `flair-core/infrastructure/` only.

| Interface | MVP implementation | Target |
| --- | --- | --- |
| `GraphStore` (Reader + Writer) | SQLite (dev/test) | PostgreSQL + Apache AGE |
| `AuthProvider` | Local dev OIDC (Dex) | Coreos go-oidc (Entra ID, Okta, Keycloak...) |
| `IngestQueue` | Direct PostgreSQL write | NATS (at scale) |

---

## Authentication model

| Actor | Method | Token lifetime |
| --- | --- | --- |
| Human user (RSSI, admin) | OIDC + Bearer JWT | 15 min access + 8h refresh |
| flair-agent | mTLS client certificate | 90 days, auto-renewed |
| Webhook receiver | HMAC-SHA256 signature | Per-request |

Agent enrollment flow: admin generates single-use token (1h TTL) → agent sends CSR → flair-core signs certificate → mTLS established.

---

## Data model

### Relational (PostgreSQL)

- `flows` — raw captured flows with all metadata
- `services` — discovered services (deduplicated by name + IP)
- `agents` — enrolled agents with certificate thumbprints
- `audit_logs` — append-only action log (never UPDATE or DELETE)
- `system_config` — key/value configuration (retention period, webhook URLs...)

### Graph (Apache AGE on same PostgreSQL instance)

- Nodes: `Service` — one per discovered endpoint
- Edges: `FLOW` — directional, carries protocol/encryption/bytes
- Primary query: cross-zone unencrypted flow detection via Cypher

---

## Security scoring

Scores are 0–100 per flow. Lower = higher risk.

| Strategy | Weight | Key signals |
| --- | --- | --- |
| TLS version | 40% | TLS 1.3 = 100, unencrypted = 0 |
| Cipher suite | 20% | Weak cipher = 0 |
| Protocol | 25% | gRPC/HTTPS = high, HTTP = low |
| Zone crossing | 15% | Same zone = 100, EXTERNAL→DATA = 0 |

Hard penalties override the weighted score:

- Unencrypted + cross-zone → max 15
- Weak cipher detected → max 25
- TLS 1.0/1.1 → max 30

Colour mapping: ≥ 70 = green, 30–69 = amber, < 30 = red.

---

## Non-negotiables

These constraints apply to every component without exception:

- No `--tls-verify=false` or equivalent anywhere
- Every `flair-core` API action → structured JSON log to stdout
- Default install works without Kubernetes, Elasticsearch, or third-party services
- Flow retention configurable via admin UI — never hardcoded
- Agents run non-root with documented minimal capabilities
- Semantic Release is authoritative for versioning — no manual tags
- `Flow` contract is versioned — any breaking change explicitly flagged across all affected repos with coordinated PRs
- Merge to `main` only when the full CI/CD pipeline is green — no exceptions
