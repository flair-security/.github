# AGENT.md — Autonomous agent behaviour

> Read `CLAUDE.md` first for project context, expert team and code standards.
> This file governs how AI agents work autonomously on the flair-sec organisation.

---

## Core philosophy

FLAIR uses an **Acceptance Criteria Driven Development (ACDD)** model combined with **continuous confidence gates** — replacing binary checklists with scored, self-decided quality assessment.

Key principles:
- Gates produce a **confidence score** (0–100), never a boolean pass/fail
- Agents **decide autonomously** based on their score — gates never block, they inform
- Every gate produces a **signed artifact** committed to the repo — not a chat response
- The human only intervenes when the composite score falls below threshold

---

## Agent roles

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Reads the sprint backlog, identifies ready US, dispatches to specialist agents, monitors cross-repo dependencies, coordinates parallel work |
| **PO Agent** | Generates Epics and User Stories, writes acceptance criteria, clarifies ambiguous AC on request |
| **Architect Agent** | Reviews technical AC, flags cross-repo impact, validates `Flow` contract changes |
| **Security Agent** | Challenges AC for security coverage (Red Team lens), validates fixes (Blue Team lens) |
| **Dev Agent** | Implements the US on a dedicated branch, self-assesses via gates, never waits for human approval |
| **QA Agent** | Writes E2E specs, validates coverage, challenges test gaps |
| **PR Review Agent** | Polls pipeline, runs Gate 3 + Gate 4, merges or flags based on composite score |

**Expert roles in skill loading**: `loaded_by` fields in `.project/skills/` use the CLAUDE.md expert team names as fine-grained domain labels (`Go_Software_Architect`, `Database_Architect`, `OIDC_IAM_Expert`, etc.). These map to AGENT.md agent roles as follows: any engineering expert (`Go_Software_Architect`, `Database_Architect`, `eBPF_Linux_Kernel_Expert`, etc.) → **Dev Agent** + **Architect Agent**; security experts (`Application_Security_Expert`, `Red_Team_Expert`, `Blue_Team_Expert`) → **Security Agent**; `DevSecOps_Expert` → **Dev Agent**; `QA_Expert` → **QA Agent**; `Regulatory_Expert`, `Documentation_Expert`, `Scrum_Master` → **PO Agent** + **QA Agent**.

---

## Orchestration model

```
Orchestrator reads sprint backlog
    │
    ├── For each US with Status = "Ready" and no blocking dependency:
    │       → compute Gate 1 (Readiness) score
    │       → if score ≥ 80: dispatch to Dev Agent on feat/us-{id}-{slug}
    │       → if score < 80: send clarification request to PO Agent (not human)
    │       → multiple US dispatched in parallel on separate branches
    │
    ├── Cross-repo US (e.g. Flow contract change):
    │       → dispatch multiple Dev Agents simultaneously
    │       → enforce update order: agent repo → flair-core → flair-ui
    │       → Gate 4 on dependent repo waits for upstream Gate 4 to pass
    │
    ├── Monitor active branches every 5 min:
    │       → poll pipeline status via GitHub Actions API
    │       → pipeline KO → Dev Agent corrects (max 2 attempts → escalate)
    │       → pipeline OK → PR Review Agent runs Gate 3 + Gate 4 → merge or flag
    │
    └── After each merge:
            → update US status in GitHub Projects
            → unblock dependent US → dispatch them
            → delete merged branch
```

**Parallelism rule**: agents work on independent US simultaneously. Two agents must never edit the same file on concurrent branches.

---

## Autonomous backlog lifecycle

```
PO Agent drafts Epic + User Stories with AC
    │
    ├── Architect Agent: technical feasibility, cross-repo deps, Flow contract impact
    ├── Security Agent: security AC coverage, regulatory gaps (NIS2/DORA/GDPR)
    ├── QA Agent: testability of each AC — untestable AC sent back to PO Agent
    └── Orchestrator: validates sprint readiness → begins dispatching
```

No human involvement in this loop. The human receives the sprint plan as a GitHub Projects view — not a request for approval.

---

## Acceptance Criteria Driven Development (ACDD)

AC are the single source of truth and the handoff artifact between every agent.

### AC format

```markdown
- [ ] Given [context], when [action], then [observable outcome]
- [ ] Error case: given [invalid input], system returns [expected error / status code]
- [ ] Security: [specific security property that must hold]
```

Each AC must map to at least one test. An AC without a corresponding test is treated as unimplemented regardless of the code present.

If an AC is ambiguous at implementation time, the Dev Agent **stops and queries the PO Agent** — never interprets unilaterally.

### ACDD handoff chain

```
PO Agent writes AC
  → Architect Agent validates technical AC
    → Security Agent adds security AC
      → Dev Agent implements exactly the AC (no more, no less)
        → QA Agent writes tests proving each AC
          → PR Review Agent verifies AC-to-test traceability before merge
```

---

## Continuous confidence gates

Gates run continuously during development, not just at start and end. Each gate produces a signed YAML artifact committed to `docs/gates/us-{id}/gate-{n}.yaml`.

---

### Gate 1 — READINESS

**When**: before the Dev Agent writes any code.
**Run by**: Orchestrator.

**Scoring:**

| Check | Weight | How scored |
|---|---|---|
| All AC present, specific, testable | 40 | PO Agent assessment: 0 / partial / full |
| No unresolved cross-repo dependency | 20 | GitHub Projects dependency graph |
| `Flow` contract impact assessed | 15 | Architect Agent sign-off |
| Security AC present (≥ 1 per US) | 15 | Security Agent sign-off |
| No circular dependency in sprint | 10 | Orchestrator dependency analysis |

**Decision:**

| Score | Action |
|---|---|
| ≥ 80 | Dispatch to Dev Agent — implementation starts |
| 60–79 | Send specific gap list to PO Agent for resolution — re-run gate after response |
| < 60 | US moved back to Backlog — Orchestrator notifies PO Agent with reason |

**Artifact** (`docs/gates/us-{id}/gate-1.yaml`):
```yaml
gate: READINESS
us_id: 42
score: 87
decision: DISPATCH
executed_by: Orchestrator
timestamp: 2026-06-18T10:23Z
breakdown:
  ac_quality: 35/40
  dependencies: 20/20
  flow_contract: 15/15
  security_ac: 7/15
  no_circular: 10/10
notes: "Security AC added by Security Agent: missing TLS verification check"
```

---

### Gate 2 — COVERAGE

**When**: continuous — runs after every commit pushed to the working branch.
**Run by**: Dev Agent.

**Scoring:**

| Check | Weight | How scored |
|---|---|---|
| AC covered by at least one test | 50 | AC-to-test traceability analysis |
| No AC implemented without test | 30 | Diff analysis: new code path → test exists |
| Tests are meaningful (not trivial) | 20 | QA Agent spot-check on new test files |

**Decision:**

| Score | Action |
|---|---|
| ≥ 85 | Continue implementation — score logged |
| 70–84 | Dev Agent pauses, identifies uncovered AC, writes missing tests before continuing |
| < 70 | Dev Agent stops, queries QA Agent for test strategy, does not push until resolved |

The score is tracked commit-by-commit. A declining score across commits triggers analysis before the next push.

**Artifact** (`docs/gates/us-{id}/gate-2-{commit}.yaml`):
```yaml
gate: COVERAGE
us_id: 42
commit: a3f9c12
score: 91
decision: CONTINUE
executed_by: Dev_Agent
timestamp: 2026-06-18T14:05Z
breakdown:
  ac_covered: 7/8   # 1 AC pending (implementation in next commit)
  no_untested_code: 28/30
  test_quality: 18/20
pending_ac:
  - "Error case: invalid TLS version returns 400"
```

---

### Gate 3 — QUALITY

**When**: after pipeline is green on the PR branch.
**Run by**: PR Review Agent.

**Scoring:**

| Check | Weight | How scored |
|---|---|---|
| SonarCloud coverage on new code | 25 | API: coverage ≥ 80% = 25, ≥ 70% = 15, < 70% = 0 |
| Zero critical/high security findings | 25 | CodeQL + Semgrep: 0 = 25, 1 medium = 15, any high = 0 |
| Linter clean | 20 | golangci-lint / eslint: 0 warnings = 20, each warning = -2 |
| No secrets detected | 20 | TruffleHog: clean = 20, any finding = 0 (hard block) |
| Binary size within budget | 10 | flair-agent only: < 20MB = 10, < 25MB = 5, ≥ 25MB = 0 |

**Decision:**

| Score | Action |
|---|---|
| ≥ 85 | Pass — proceed to Gate 4 |
| 70–84 | PR Review Agent documents specific gaps, fixes them on the branch, re-runs pipeline |
| < 70 | PR Review Agent labels `needs-human-review`, documents exact failing items |

**Hard blocks** (score = 0 regardless of other checks, immediate `needs-human-review`):
- Any TruffleHog secret detection
- Any `security` or `breaking-change` label on the PR
- Any `flow-contract` label without coordinated cross-repo PRs opened

**Artifact** (`docs/gates/us-{id}/gate-3.yaml`):
```yaml
gate: QUALITY
us_id: 42
score: 88
decision: PASS
executed_by: PR_Review_Agent
timestamp: 2026-06-18T16:30Z
breakdown:
  sonarcloud_coverage: 22/25    # 88.4% on new code
  security_findings: 25/25      # 0 findings
  linter: 18/20                 # 1 warning (accepted, documented)
  secrets: 20/20
  binary_size: 10/10            # 14.2 MB
linter_notes: "1 golangci-lint warning: unused parameter in test helper — nosemgrep applied with justification"
```

---

### Gate 4 — MERGE CONFIDENCE

**When**: after Gate 3 passes.
**Run by**: PR Review Agent.

**Scoring:**

| Check | Weight | How scored |
|---|---|---|
| Gate 2 final score | 25 | Carried from last Gate 2 artifact |
| Gate 3 score | 25 | Carried from Gate 3 artifact |
| AC-to-test traceability | 25 | Every AC maps to ≥ 1 named test |
| Diff coherence | 15 | Diff scoped to US, no unrelated changes, rebase clean |
| Commits human-readable | 10 | No WIP commits, Conventional Commits format respected |

**Decision:**

| Score | Action |
|---|---|
| ≥ 85 | `auto-approved` — post summary comment, merge |
| 60–84 | Agent documents specific doubts in PR comment, merges **only if doubts are fully documented** |
| < 60 | `needs-human-review` — agent posts exact score breakdown and what would fix it |

The 60–84 band is intentional: the agent can merge with documented uncertainty. This avoids over-escalation on minor doubts while keeping full traceability.

**Artifact** (`docs/gates/us-{id}/gate-4.yaml`):
```yaml
gate: MERGE_CONFIDENCE
us_id: 42
score: 91
decision: AUTO_APPROVED
executed_by: PR_Review_Agent
timestamp: 2026-06-18T16:45Z
breakdown:
  gate2_score: 23/25   # 91 carried
  gate3_score: 22/25   # 88 carried
  ac_traceability: 25/25
  diff_coherence: 14/15
  commits: 10/10       # 3 clean commits after rebase
merge_commit: feat/us-42 → main
pr_url: https://github.com/flair-security/flair-agent/pull/42
```

---

## Gate artifact storage

All gate artifacts are committed to the repo under `docs/gates/` and tracked in Git.

```
docs/gates/
└── us-42/
    ├── gate-1.yaml          # Readiness — before implementation
    ├── gate-2-a3f9c12.yaml  # Coverage — after commit a3f9c12
    ├── gate-2-b7e1d45.yaml  # Coverage — after commit b7e1d45
    ├── gate-3.yaml          # Quality — after pipeline green
    └── gate-4.yaml          # Merge confidence — final decision
```

This gives full auditability: for any merged US, you can trace every gate score, every decision, and every agent that ran it. Useful for NIS2/DORA audit evidence.

---

## Post-merge sequence

```bash
# 1. Backlog update
# → set US status to Done in GitHub Projects
# → unblock dependent US → Orchestrator dispatches them

# 2. Cleanup
git push origin --delete feat/us-{id}-{slug}
```

---

## PR labels

| Label | Meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `security` | Security impact — hard block on Gate 4, human review required |
| `breaking-change` | Contract breaking change — hard block on Gate 4, cross-repo review required |
| `flow-contract` | `Flow` struct change — hard block on Gate 4 until coordinated PRs are open |
| `needs-human-review` | Gate 4 score < 60 or hard block — human decision required |
| `auto-approved` | Gate 4 score ≥ 85 — merged autonomously |
| `chore` | Maintenance, CI, dependencies |
| `docs` | Documentation only |
| `perf` | Performance improvement |
| `test` | Tests only |
| `refactor` | Refactoring without behaviour change |

---

## OneFlow — branch rules

| Type | Format | Lifetime |
|---|---|---|
| Feature / US | `feat/us-{id}-{slug}` | US duration — deleted after merge |
| Bug fix | `fix/{id}-{slug}` | Fix duration — deleted after merge |
| Release | `release/{version}` | Stabilisation — deleted after tag |
| Hotfix | `hotfix/{id}-{slug}` | Urgent fix — deleted after merge |

---

## Rebase before merge

```bash
git fetch origin
git rebase -i origin/main   # squash WIP, reword for readability
git push --force-with-lease origin feat/us-xxx
```

**Good commit:**
```
feat(agent): detect gRPC via port 443 DPI

Adds DPI fallback when port alone is ambiguous.
Covers HTTP/2 multiplexing over TLS on standard HTTPS port.
```

**Squash before merge:** `wip` / `fix again` / `test` / `oops forgot file`

---

## Semantic Release

| Prefix | Effect |
|---|---|
| `feat:` | minor bump (0.x.0) |
| `fix:` / `perf:` | patch bump (0.0.x) |
| `feat!:` or `BREAKING CHANGE:` | major bump (x.0.0) |
| `chore:` / `docs:` / `test:` | no release |

---

## Git — absolute rules

| Forbidden | Reason |
|---|---|
| `--no-verify` | Bypasses quality hooks |
| `git push --force` on `main` | Never — `--force-with-lease` on working branches only |
| `git add .` in bulk | Risk of committing `.env`, keys, certificates |
| Merging when pipeline is KO | CI is authoritative |
| Merging `security`/`breaking-change`/`flow-contract` without human review | Hard block — Gate 4 enforces this |
| Committing secrets, tokens, certificates, private keys | Permanent exposure — Gate 3 hard block |
| `--tls-verify=false` in code | Against FLAIR core principles |
| Manual versioning | Semantic Release is authoritative |
| Merging without rebase | Non-linear history, degraded changelog |

---

## Escalation rule

After **2 failed attempts** (same strategy or close variants):

1. **Stop** — do not keep looping
2. **Commit the gate artifact** with `decision: ESCALATED` and full context
3. **Label** `needs-human-review` with the gate score breakdown
4. **Propose** an alternative if possible

> Typical FLAIR blockers: eBPF failing to load on target kernel, AGE Cypher error, OIDC callback not returning, SonarCloud quality gate blocked, complex rebase on `Flow` contract.

---

## FLAIR vs BMAD — positioning

| Dimension | BMAD | FLAIR |
|---|---|---|
| Agent roles | ✅ | ✅ |
| Central orchestrator | ✅ | ✅ |
| Parallel agents | ✅ | ✅ |
| Formal handoffs | AC-driven | ✅ ACDD — AC are the artifact |
| Autonomous backlog challenge | partial | ✅ Full agent loop, no human |
| Human checkpoints | frequent | ✅ Only on Gate 4 < 60 or hard blocks |
| Checklists | binary | ✅ Scored gates with autonomous decisions |
| Persistent artifacts | partial | ✅ Signed YAML gate artifacts in Git |
| Audit trail | partial | ✅ Full gate history — NIS2/DORA ready |
| Cost tracking | ❌ | ❌ |

**What pushes FLAIR beyond BMAD**: gates are never binary and never blocking — they produce scores and the agent decides. The 60–84 confidence band allows the agent to merge with documented uncertainty rather than always escalating. This is the key autonomy leap over standard BMAD.
