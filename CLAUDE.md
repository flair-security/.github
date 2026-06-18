# CLAUDE.md — flair-sec organisation

> Central context for all AI work on the flair-sec organisation.
> Covers the `.github` repo (org profile, backlog, governance) and provides the shared framework for all repos.
> Each repo has its own `CLAUDE.md` with repo-specific conventions — read this file first.
>
> Also read: `AGENT.md` (autonomous behaviour)

---

## Communication style

Concise and direct. Technically precise. No unnecessary recaps.

**Exceptions — structured responses with full context:**
- Writing or reviewing User Stories / Epics
- Cross-repo architecture decisions (the `Flow` contract)
- Security or regulatory advice, or irreversible actions (explicit confirmation required)
- Creating or updating the GitHub Projects backlog

---

## Session initialisation

`CLAUDE.md` is loaded automatically — do not re-read it.

Read the following docs **only when the task requires it:**

| Doc | Read when… |
|---|---|
| `profile/README.md` | modifying the GitHub organisation profile |
| `.github/ISSUE_TEMPLATE/` | creating or modifying issue templates |
| `docs/ARCHITECTURE.md` | cross-repo decision, modifying the `Flow` contract |
| `docs/ADR/` | consulting or creating an Architecture Decision Record |
| `SECURITY.md` | anything related to vulnerability disclosure |
| `AGENT.md` | working in autonomous mode (PR, pipeline, merge) |

---

## Project identity

- **Name**: FLAIR — Flow and Link Analysis with Inspection Report
- **Mission**: map application flows, detect protocols, fingerprint TLS encryption — for security engineers, RSSIs and auditors
- **Licence**: GPL v3 (agents + core) / Apache 2.0 (UI, Helm, Terraform, SDKs) / CC0 (rules) / CC BY 4.0 (docs)
- **Deployment model**: self-hosted, single-tenant per organisation. No SaaS multi-tenancy.
- **Code language**: English (code, comments, commits, issues). French accepted in PO conversations.

---

## Ecosystem — repos and technologies

| Repo | Role | Technologies |
|---|---|---|
| `flair-agent` | Linux eBPF agent — capture, protocol, TLS | Go, C, eBPF (`cilium/ebpf`), libbpf |
| `flair-core` | Central server — graph, scoring, REST API, auth | Go, PostgreSQL, Apache AGE, `coreos/go-oidc`, swaggo |
| `flair-ui` | Web interface — flow map, RSSI dashboard | Angular, TypeScript, D3.js, RxJS |
| `flair-helm` | Helm chart — DaemonSet + core in one command | Helm, Kubernetes YAML |
| `flair-docs` | Documentation — architecture, deployment, API | Docusaurus, Markdown |
| `flair-agent-windows` | Windows agent — ETW + Npcap | Go, ETW, Npcap, `go-etw` |
| `flair-agent-k8s` | Kubernetes-native sidecar agent | Go, eBPF, Kubernetes API |
| `flair-terraform-aws` | AWS Terraform modules | Terraform (HCL), AWS SDK |
| `flair-terraform-azure` | Azure Terraform modules | Terraform (HCL), Azure SDK |
| `flair-terraform-gcp` | GCP Terraform modules | Terraform (HCL), GCP SDK |
| `flair-sdk-go` | Go client for the flair-core API | Go |
| `flair-sdk-python` | Python client for the flair-core API | Python |
| `flair-rules` | Community detection and scoring rules | YAML |

**Absolute rule: never cross repo responsibilities.**
An agent contains no scoring logic. `flair-core` does no packet capture. `flair-ui` never talks directly to agents.

---

## Local development environment

Local dev uses **Docker Desktop** (Windows/Mac). Each repo provides a `docker-compose.dev.yml`.

```bash
docker compose -f docker-compose.dev.yml up
```

### eBPF constraint on Docker Desktop

`flair-agent` requires access to a Linux kernel. On Docker Desktop, eBPF runs inside the intermediate Linux VM — sufficient for unit and functional tests. Full validation (performance, kernel compatibility, network namespaces) requires a dedicated Linux server.

**Rule**: dev and unit tests on Docker Desktop, full eBPF validation on a Linux test server.

| Repo | Dev Docker services |
|---|---|
| `flair-core` | PostgreSQL + Apache AGE, core in watch mode |
| `flair-ui` | Angular dev server (hot reload), proxy to flair-core |
| `flair-agent` | Privileged Linux container with host kernel access |
| Org `.github` | None — governance repo only |

---

## Shared data contract — `Flow`

The `Flow` struct is the central interface between all agents and `flair-core`.
**Any change here is a cross-repo breaking change — explicit versioning required.**

Update order: **agent (producer) → flair-core (consumer/storage) → flair-ui (display)**.
Always open coordinated PRs and explicitly flag cross-repo impact.

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
                                   // populated manually or via CMDB connector
}
```

`Metadata` is intentionally open — do not add dedicated columns for concepts that belong here.
Optional fields (`ContainerID`, `JA3Hash`, `TLSCipherSuite`): zero value is acceptable, never make them blocking for a minimal agent.

---

## AI expert team

Each contribution mobilises the relevant experts. Mention them explicitly in the response.

| Expert | Domain |
|---|---|
| **Go Software Architect** | Package architecture, interfaces, patterns (Repository, Factory, Strategy), SOLID, coupling/cohesion |
| **Database Architect** | PostgreSQL + Apache AGE schema, graph model, indexes, migrations, referential integrity |
| **eBPF / Linux Kernel Expert** | eBPF C programs, `cilium/ebpf`, Linux capabilities, network namespaces, kernel edge cases |
| **Application Security Expert** | TLS/JA3 fingerprinting, DPI, anomaly detection, security scoring |
| **DevSecOps Expert** | GitHub Actions, Semgrep, CodeQL, SonarCloud, SBOM, GPG signatures, Semantic Release |
| **Red Team Expert** | Attack vectors (flow injection, compromised agent, API abuse), OWASP |
| **Blue Team Expert** | Hardening, mTLS, capabilities, audit logs, Red Team response |
| **OIDC / IAM Expert** | OIDC, SAML via broker, agent enrolment, token management |
| **Kubernetes / Helm Expert** | DaemonSet, Pod Security Admission, RBAC, Helm chart, sidecar patterns |
| **Terraform Expert** | Multi-cloud modules (AWS/Azure/GCP), provisioning, cloud-native identities |
| **Angular Frontend Expert** | Angular, strict TypeScript, RxJS, D3.js, WCAG 2.1 AA accessibility |
| **Regulatory Expert** | NIS2, DORA, ISO 27001, GDPR (flows contain personal data) |
| **Product Owner** | GitHub Projects backlog, Epics, User Stories, acceptance criteria, prioritisation |
| **Scrum Master** | Cross-repo coordination, sprints, impediments, backlog consistency |
| **QA Expert** | Test strategy (unit/integration/E2E), coverage, non-regression |
| **Documentation Expert** | Docusaurus, deployment guides, API reference, integration cookbook |

---

## Calling experts

| Task type | Expert(s) |
|---|---|
| Go package architecture, interfaces, patterns | **Go Software Architect** |
| DB schema, graph, PostgreSQL/AGE migrations | **Database Architect** |
| eBPF programs, packet capture, capabilities | **eBPF / Linux Kernel Expert** |
| TLS fingerprinting, scoring, protocol detection | **Application Security Expert** |
| Security vulnerability, attack vector | **Red Team Expert** → **Blue Team Expert** |
| OIDC auth, agent enrolment, tokens | **OIDC / IAM Expert** |
| CI/CD, SAST, SonarCloud, SBOM, Semantic Release | **DevSecOps Expert** |
| Kubernetes, Helm, DaemonSet | **Kubernetes / Helm Expert** |
| Terraform, cloud provisioning | **Terraform Expert** |
| Angular, D3.js, flow map interface | **Angular Frontend Expert** |
| NIS2, DORA, GDPR | **Regulatory Expert** |
| Backlog, user stories, acceptance criteria | **Product Owner** |
| Tests, coverage, non-regression | **QA Expert** |
| Documentation, guides, API reference | **Documentation Expert** |
| Modifying the `Flow` contract | **Go Software Architect** + **eBPF Expert** + **Angular Expert** |
| Unknown-origin bug | **Go Software Architect** first, then **Red Team Expert** if security suspected |

**Rules:**
- Always mention the expert explicitly when their domain is involved.
- Any Red Team finding must be fixed by the Blue Team **before any merge**.
- A `Flow` contract change requires all three chain experts without exception.

---

## Before starting a User Story — mandatory PO validation

Before any implementation, explicitly confirm two points with the PO:

**1. The US itself** — confirm it is the right one to work on next:
> "I'm about to implement `us-{slug}` (priority X, estimate Y).
> Please confirm this is the next one to work on, or redirect me."

**2. Acceptance criteria** — present the planned criteria and wait for approval before writing any production code:
> "Here are the acceptance criteria I plan to implement: [list].
> Do you validate, or do you want to add / modify / remove any?"

**Why**: acceptance criteria define the exact implementation scope. A poorly framed criterion upfront means code to rewrite. The PO validates criteria **before** any production code is written.

**Exceptions** (no consultation required):
- Security fixes on existing code with an immediately exploitable vector
- Syntax / linter / broken test fixes blocking CI
- Bug fixes with a clearly identified root cause and no ambiguous scope

---

## Task order per User Story

For each feature or fix, follow this order **without exception:**

| Step | Content |
|---|---|
| **1. Code** | Implement (service, handler, repository…) + GoDoc / TSDoc |
| **2. Tests** | Write unit + integration tests covering all branches — **in the same commit** |
| **3. Quality** | Linter and static analysis must be green |
| **4. UI / templates** | Angular components, templates, styles |
| **5. Backlog** | Create the US if not tracked · update status in GitHub Projects · **required before commit** |
| **6. E2E** | Write and run E2E spec (happy path + 1 critical error path) |
| **7. Commit** | `git add` file by file · atomic commits · on the dedicated branch |

> **E2E deferral**: if the test environment is unavailable, E2E can be deferred to the next session. Steps 5 and 7 are never deferrable.
>
> **Tests approach**: write code first, then tests covering all branches and edge cases. Strict TDD (Red → Green → Refactor) is **not used**. Exception: when an API or service contract is unclear, write tests first to force clarification of expected behaviour before implementing.

---

## Action parallelisation

Run as many independent actions in parallel as possible in each turn to accelerate development:

| Parallelisable actions | Examples |
|---|---|
| Independent reads | Multiple file reads / grep / glob in the same turn |
| Linters | `golangci-lint` + `go vet` launched simultaneously |
| Independent file writes | Multiple files in parallel (e.g. unit tests + integration tests for the same feature) |
| Codebase searches | Multiple grep on different targets |

Only sequence steps that depend on the result of a previous one.

---

## Code standards

### Go (`flair-agent`, `flair-core`, `flair-sdk-go`)
- GoDoc required on all exported functions and methods
- `gofmt` + `golangci-lint` — no warning ignored without a commented justification
- Explicit error handling — no `_` on returned errors
- No global init with side effects — dependencies passed explicitly

### Angular (`flair-ui`)
- Strict TypeScript — no `any`
- OnPush change detection by default
- RxJS for async — no Promise except for interop
- WCAG 2.1 AA on all interactive elements

### Terraform (`flair-terraform-*`)
- `terraform fmt` + `terraform validate` before every commit
- No hardcoded values — all via typed, described variables

### General
- Conventional Commits: `type(scope): message`
  - Types: `feat` | `fix` | `chore` | `docs` | `refactor` | `test` | `ci` | `perf` | `security`
- Co-author on every commit: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- No secrets in code — environment variables or secret manager
- `--tls-verify=false` or equivalent: **forbidden everywhere, no exception**
- Every `flair-core` API action → structured JSON log line to stdout

### Quality annotations
- SonarCloud false positives: `// NOSONAR — <short justification>` (justification required)
- Semgrep false positives: `// nosemgrep: <rule-id>`

---

## CI/CD pipeline

Sequential GitHub Actions pipeline — a failure blocks all subsequent steps.

```
push / PR
    │
    ├── 1. Build          compile binary / Docker image + size check (flair-agent: < 20 MB)
    ├── 2. Tests          unit / integration / E2E + SonarCloud coverage gate
    ├── 3. Quality        lint + format + static analysis
    ├── 4. Security audit Semgrep + CodeQL + TruffleHog + Dependabot SBOM
    ├── 5. Publish        push Docker image + release artefacts
    └── 6. Deploy         Semantic Release + GPG signatures + deployment (main only)
```

**SonarCloud** (open source, free): quality gate blocks if coverage < 80% on new code, new security/reliability issues, or duplications > 3%.

**Rule**: merge to `main` only when the entire pipeline is green. No exceptions, including `chore:` or `docs:` commits.

---

## Backlog — GitHub Projects

Reference repo: **`https://github.com/flair-security/.github`**

The Project aggregates issues from all repos into a single unified view.

### Sprints

Sprints are **prioritisation groups** with no fixed duration. A sprint closes when its User Stories are merged to `main`.

Priority order (descending):
1. Security (vulnerability, FLAIR non-negotiable)
2. Cross-repo contract breaking (unblocking)
3. Core functional value (MVP)
4. Quality, tests, documentation

### Issue hierarchy

```
Epic (parent issue, label "epic")
└── User Stories / Enablers (child issues, linked via "tracked by")
```

### User Story template (`.github/ISSUE_TEMPLATE/user-story.md`)

```markdown
**As a** [RSSI / auditor / security engineer / admin]
**I want** [action]
**So that** [business or security benefit]

**Acceptance criteria**
- [ ] ...
- [ ] ...

**Target repo**: flair-{agent|core|ui|...}
**Estimate**: XS / S / M / L / XL
**Dependencies**: #xxx (if applicable)
```

### Project custom fields

| Field | Type | Values |
|---|---|---|
| Status | Single select | Backlog / Ready / In progress / Review / Done |
| Priority | Single select | Critical / High / Medium / Low |
| Repo | Single select | flair-agent / flair-core / flair-ui / ... |
| Phase | Single select | MVP / v1-enterprise / phase-3 |
| Size | Single select | XS / S / M / L / XL |
| Sprint | Iteration | prioritisation groups, no fixed duration |

**If an untracked need is expressed**, the PO/Scrum Master must immediately:
1. Identify the relevant Epic (or create one)
2. Create the US issue with the full template
3. Add it to the Project with the correct fields
4. Signal before continuing implementation

Never implement without a traceable issue.

---

## Audits

In `docs/audits/` of the `.github` repo — one file per category, updated in place. Never create dated files.

| Category | File |
|---|---|
| Application security | `audits/audit-cyber.md` |
| eBPF / Kernel | `audits/audit-ebpf.md` |
| Software architecture | `audits/audit-architecture.md` |
| Database / Graph | `audits/audit-bdd.md` |
| CI/CD / DevSecOps | `audits/audit-cicd.md` |
| QA / Tests | `audits/audit-qa.md` |
| Regulatory (NIS2/DORA/GDPR) | `audits/audit-reglementaire.md` |
| Documentation | `audits/audit-docs.md` |

Revision history at the bottom of each file:
```markdown
## Revision history

| Version | Date | Score | Key changes |
|---|---|---|---|
| v1 | YYYY-MM-DD | X.X/10 | Initial audit |
```

**Forbidden:**
- ❌ Creating `audit-cyber-2026-06-18.md` → always update `audit-cyber.md`
- ❌ Creating any audit file outside `docs/audits/`

---

## FLAIR non-negotiables

These apply to all repos without exception:

- No `--tls-verify=false` or equivalent, anywhere, ever
- Every `flair-core` API action → structured JSON log to stdout
- Default install works without Kubernetes, without Elasticsearch, without calling third-party services
- Flow retention policy configurable via admin UI — never hardcoded
- Agents run non-root with documented minimal Linux capabilities
- `Flow` contract versioned — any breaking change explicitly flagged cross-repos
- Semantic Release is authoritative — no manual tags
- Merge to `main` only when the full CI/CD pipeline is green

---

## Escalation rule

If the AI fails to resolve a problem after **2 attempts** (same strategy or close variants):

1. **Stop** — do not continue looping
2. **Report**: describe the blocker, what was tried, why it failed
3. **Propose** an alternative: different approach, different tool, workaround, or hand off to the human

Also applies to pipeline corrections: after 2 failed CI fix attempts, set the `needs-human-review` label and describe the blocker.

> Typical FLAIR blockers: eBPF program failing to load on target kernel, AGE not responding to Cypher queries, OIDC callback not returning, SonarCloud quality gate blocked, complex rebase conflicts on the `Flow` contract.
