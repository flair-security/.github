# US-{{ id }} — {{ title }}

> **Story file** — single source of truth for this User Story.
> Loaded by every agent working on this US. Never summarise — always read in full.
> Lives in `flair-docs/stories/us-{{ id }}.md`

---

## Identity

| Field | Value |
|---|---|
| **US ID** | US-{{ id }} |
| **Epic** | {{ epic_title }} (#{{ epic_id }}) |
| **Target repo(s)** | {{ repos }} |
| **Phase** | {{ MVP / v1-enterprise / phase-3 }} |
| **Estimate** | {{ XS / S / M / L / XL }} |
| **Sprint** | {{ sprint_id }} |
| **Status** | {{ Backlog / Ready / In progress / Review / Done }} |
| **Assigned agent** | {{ Dev_Agent / unassigned }} |
| **Dependencies** | {{ #us-id list or "none" }} |
| **Blocks** | {{ #us-id list or "none" }} |

---

## User Story

**As a** {{ role: RSSI / auditor / security engineer / admin }}
**I want** {{ action }}
**So that** {{ business or security benefit }}

---

## Context & motivation

{{ 2-4 sentences explaining WHY this US exists, what problem it solves, and how it fits in the broader Epic. Written by the PO Agent. }}

---

## Acceptance Criteria

Each AC has a unique ID, a Given/When/Then statement, and a test mapping.
An AC without a test mapping is treated as unimplemented regardless of code present.

```
AC-{{ id }}-01
  Given: {{ context }}
  When:  {{ action }}
  Then:  {{ observable outcome }}
  Test:  {{ test file path }}::{{ test function name }}
  Type:  {{ unit / integration / e2e }}

AC-{{ id }}-02
  Given: {{ context — error case }}
  When:  {{ invalid input or edge case }}
  Then:  {{ expected error, status code, log output }}
  Test:  {{ test file path }}::{{ test function name }}
  Type:  {{ unit / integration }}

AC-{{ id }}-SEC-01
  Given: {{ security context }}
  When:  {{ action that must be secure }}
  Then:  {{ specific security property: TLS version, auth check, audit log entry... }}
  Test:  {{ test file path }}::{{ test function name }}
  Type:  {{ unit / integration }}
```

**AC coverage rule**: every AC-{id}-xx entry must have a `Test:` field populated before the PR is opened. Empty `Test:` field = Gate 2 score deduction.

---

## Technical design

*Written by the Architect Agent before implementation starts.*

### Affected components

| Component | Repo | Change type |
|---|---|---|
| {{ e.g. EBPFCollector }} | {{ flair-agent }} | {{ new / modified / deleted }} |
| {{ e.g. GraphStore interface }} | {{ flair-core }} | {{ new / modified / deleted }} |

### Flow contract impact

- [ ] This US modifies the `Flow` struct → coordinated PRs required (agent → core → ui)
- [ ] This US adds a new `Metadata` key: `{{ key }}` — document in `docs/ARCHITECTURE.md`
- [ ] No `Flow` contract impact

### Design decisions

{{ Brief ADR-style notes: what was considered, what was chosen, why. 
   Reference existing ADRs if applicable: docs/ADR/adr-{id}.md }}

### Interface sketch

```go
// For Go repos — sketch the key interface or struct change
// Not full implementation — just the contract the Dev Agent must honour

type {{ InterfaceName }} interface {
    {{ MethodName }}(ctx context.Context, {{ params }}) ({{ returns }}, error)
}
```

```typescript
// For flair-ui — sketch the Angular component or service contract
```

---

## Security assessment

*Written by the Security Agent before implementation starts.*

### Threat model for this US

| Threat | Vector | Mitigation in AC |
|---|---|---|
| {{ e.g. Unencrypted flow data }} | {{ e.g. agent → core transport }} | {{ AC-id-SEC-01 }} |

### Regulatory mapping

| Requirement | Framework | Covered by |
|---|---|---|
| {{ e.g. Network flow mapping }} | {{ NIS2 Art. 21 }} | {{ AC-id-01 }} |

### Security AC completeness checklist

*Run by Security Agent — scored, not boolean.*

- [ ] Authentication checked (every API endpoint has auth AC)
- [ ] TLS version validated (no cleartext, no TLS 1.2 unless documented exception)
- [ ] Audit log entry defined for every state-changing operation
- [ ] Input validation covered (every external input has a validation AC)
- [ ] Error responses defined (no stack traces leaked, consistent error format)
- [ ] `--tls-verify=false` or equivalent: confirmed absent

---

## Implementation notes

*Written by the Dev Agent during implementation. Updated commit-by-commit.*

### Approach

{{ Dev Agent documents their implementation approach before writing code.
   References the interface sketch above. Flags any deviation from the design. }}

### Files created / modified

| File | Change | Commit |
|---|---|---|
| {{ path }} | {{ created / modified }} | {{ short SHA }} |

### Deviations from design

{{ Any deviation from the Architect Agent's design sketch must be documented here
   with justification. Undocumented deviations = Gate 2 score deduction. }}

---

## Test mapping (AC traceability)

*The single source of truth for Gate 2 and Gate 4 scoring.*

| AC ID | Test file | Test function | Type | Status |
|---|---|---|---|---|
| AC-{{ id }}-01 | `{{ path/to/test_file.go }}` | `{{ TestFunctionName }}` | unit | ⬜ pending / ✅ passing |
| AC-{{ id }}-02 | `{{ path/to/test_file.go }}` | `{{ TestErrorCase }}` | integration | ⬜ pending / ✅ passing |
| AC-{{ id }}-SEC-01 | `{{ path/to/test_file.go }}` | `{{ TestSecurityProperty }}` | unit | ⬜ pending / ✅ passing |

**Convention**: test functions must include the AC ID in their name or docstring.
Example: `func TestEBPFCollector_AC42_01_DetectsGRPCProtocol(t *testing.T)`

---

## Gate artifacts

| Gate | Score | Decision | Artifact | Timestamp |
|---|---|---|---|---|
| Gate 1 — Readiness | — | — | `docs/gates/us-{{ id }}/gate-1.yaml` | — |
| Gate 2 — Coverage (latest) | — | — | `docs/gates/us-{{ id }}/gate-2-{sha}.yaml` | — |
| Gate 3 — Quality | — | — | `docs/gates/us-{{ id }}/gate-3.yaml` | — |
| Gate 4 — Merge confidence | — | — | `docs/gates/us-{{ id }}/gate-4.yaml` | — |

---

## PR & merge

| Field | Value |
|---|---|
| Branch | `feat/us-{{ id }}-{{ slug }}` |
| PR URL | — |
| PR labels | — |
| Merge commit | — |
| Merged at | — |
| Merged by | — |

---

## Post-merge notes

{{ Any follow-up US created as a result of this implementation.
   Known technical debt introduced (documented, not ignored).
   Observations for the Orchestrator about sprint dependencies. }}
