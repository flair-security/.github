# Contributing to FLAIR

Thank you for your interest in contributing to FLAIR.
FLAIR is an open source project built by and for security engineers, RSSIs and auditors.

---

## Table of contents

- [Code of Conduct](#code-of-conduct)
- [What we are building](#what-we-are-building)
- [Ways to contribute](#ways-to-contribute)
- [Development environment](#development-environment)
- [Development workflow](#development-workflow)
- [Code standards](#code-standards)
- [Submitting a pull request](#submitting-a-pull-request)
- [Security vulnerabilities](#security-vulnerabilities)
- [Getting help](#getting-help)

---

## Code of Conduct

We expect all contributors to be respectful and constructive.
We do not tolerate harassment, discrimination or bad-faith engagement of any kind.
Violations can be reported to the maintainers via GitHub private message.

---

## What we are building

FLAIR maps application network flows, detects protocols and fingerprints TLS encryption —
for security teams that need to answer *"is our infrastructure secure?"* in under 60 seconds.

Before contributing a feature, ask: does this help a RSSI or auditor understand their
security posture faster? If yes, it is likely a good fit for FLAIR.

---

## Ways to contribute

### Report a bug
Open a [bug report](.github/ISSUE_TEMPLATE/bug_report.yml).
Include your FLAIR version, platform, kernel version and structured JSON logs.

### Suggest a feature
Open a [feature request](.github/ISSUE_TEMPLATE/feature_request.yml).
Describe the security problem you are trying to solve — not just the implementation.

### Contribute a detection rule
The easiest way to contribute. Rules live in `flair-rules` (CC0 — no CLA required).
See `flair-rules/CONTRIBUTING.md` for the rule format.

### Fix a bug or implement a feature
See the [Development workflow](#development-workflow) section below.

### Improve documentation
Documentation lives in `flair-docs`. Docusaurus markdown — no build step required for
content contributions.

---

## Development environment

### Prerequisites

- **Docker Desktop** (Windows or Mac) or **Docker Engine** (Linux)
- **Git** with Conventional Commits discipline
- **Go 1.22+** (for `flair-agent` and `flair-core`)
- **Node.js 20+** (for `flair-ui` and `flair-docs`)
- **Python 3.12+** (for utility scripts)

### Starting the local stack

Each repo provides a `docker-compose.dev.yml`:

```bash
# Start flair-core + PostgreSQL + AGE + local OIDC (Dex)
cd flair-core
docker compose -f docker-compose.dev.yml up

# In another terminal — start flair-ui
cd flair-ui
docker compose -f docker-compose.dev.yml up
```

### eBPF development note

`flair-agent` requires a Linux kernel with `CAP_NET_ADMIN` and `CAP_SYS_PTRACE`.
On Docker Desktop (Windows/Mac), eBPF runs inside the Docker VM — sufficient for
unit tests and functional tests.
Full kernel compatibility testing requires a Linux host or VM.

---

## Development workflow

FLAIR uses **OneFlow** — a single `main` branch with short-lived feature branches.

### 1. Find or create an issue

All work starts from a GitHub issue.
If you are working on an existing issue, comment to signal intent.
If you are proposing new work, open an issue first and wait for maintainer acknowledgement
before spending time on implementation.

### 2. Create a branch

```bash
git checkout main
git pull origin main
git checkout -b feat/us-{issue-id}-{short-description}
# Examples:
# feat/us-42-grpc-detection
# fix/43-cursor-pagination
```

### 3. Implement with AC coverage

Every issue has acceptance criteria. Your implementation must cover every AC.
Name your test functions with the AC ID:

```go
// Go
func TestEBPFCollector_AC42_01_DetectsGRPCOnPort443(t *testing.T) {}
```

```typescript
// Angular
it('AC-42-01: renders unencrypted flows in red', () => {});
```

Tests are written in the same commit as the code they cover — never deferred.

### 4. Rebase before opening a PR

```bash
git fetch origin
git rebase -i origin/main
# Squash WIP commits — each final commit must be human-readable
git push --force-with-lease origin feat/us-42-grpc-detection
```

No merge commits. No `wip`, `fix again` or `test` commits in the final branch.

### 5. Open a pull request

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
Fill in every section — especially the AC coverage table.

---

## Code standards

Full standards are in `CLAUDE.md`. The key rules:

**Go**
- GoDoc on all exported symbols
- `gofmt` + `golangci-lint` must be clean
- Explicit error handling — no `_` on returned errors
- No global init with side effects

**Angular / TypeScript**
- Strict TypeScript — no `any`
- OnPush change detection by default
- WCAG 2.1 AA on all interactive elements

**All languages**
- Conventional Commits: `type(scope): message`
- No `--tls-verify=false` or equivalent — ever
- No secrets in code

---

## Submitting a pull request

### CI must be green

All CI checks must pass before a PR can be merged:
1. Build
2. Tests (unit + integration + E2E where applicable)
3. Quality (lint + static analysis)
4. Security audit (Semgrep + CodeQL + TruffleHog)

SonarCloud quality gate: ≥ 80% coverage on new code.

### Review process

- PRs are reviewed by maintainers within 48 hours
- Security-impacting changes require an additional review from the security team
- Changes to the `Flow` contract require coordinated PRs across all affected repos

### Commit co-authorship

If you used an AI assistant to write part of your contribution, add a co-author line:

```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

This is encouraged — we believe in transparent AI-assisted development.

---

## Security vulnerabilities

**Do not open a public issue for security vulnerabilities.**

Report via [GitHub Private Vulnerability Reporting](https://github.com/flair-security/.github/security/advisories/new)
or see [SECURITY.md](SECURITY.md) for the full disclosure policy.

---

## Getting help

- **GitHub Discussions** — architecture questions, feature ideas, general discussion
- **Issues** — bug reports and feature requests only
- **GitHub Security Advisories** — vulnerabilities only

We are a small team. Response times may vary but we read everything.
