# CLAUDE.md — flair-rules

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: YAML, JSON Schema  
**Role**: Community scoring and detection rules — loaded by flair-core ScoringEngine  
**Licence**: CC0 (public domain — rules are community-contributed)

---

## Build & test commands

```bash
# Validate rule syntax
python3 scripts/validate-rules.py rules/

# Run rules against test fixtures
python3 scripts/test-rules.py rules/ testdata/

# Schema validation (requires ajv-cli)
ajv validate -s schemas/rule.schema.json -d rules/**/*.yaml

# Lint YAML
yamllint rules/
```

---

## Repo structure

```
flair-rules/
  rules/
    network/            ← lateral movement, port scans, beacon patterns
    tls/                ← weak cipher, expired cert, JA3 blacklist
    protocols/          ← protocol anomalies, tunneling, DNS exfil
    regulatory/         ← NIS2, GDPR data flow rules
  testdata/             ← Flow fixtures (JSON) for rule tests
  schemas/
    rule.schema.json    ← JSON Schema for rule validation
  scripts/
    validate-rules.py
    test-rules.py
```

---

## Rule format

```yaml
id: FLAIR-NET-001
name: Lateral movement — internal SMB sweep
severity: high         # critical | high | medium | low | info
category: lateral-movement
description: |
  Detects when a single source IP connects to more than 10 internal
  destinations on port 445 within 60 seconds.
condition:
  flow:
    dst_port: 445
    direction: internal
  aggregate:
    group_by: src_ip
    count_distinct: dst_ip
    window_seconds: 60
    threshold: ">= 10"
mitre:
  tactic: lateral-movement
  technique: T1021.002   # Remote Services: SMB/Windows Admin Shares
tags: [smb, lateral-movement, windows]
references:
  - "https://attack.mitre.org/techniques/T1021/002/"
```

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-ac-traceability | all US |
| 2 | skill-security-scoring | scoring logic / new rule categories |

---

## Repo-specific rules

- Rule IDs follow format: `FLAIR-{CATEGORY}-{NNN}` — never reuse a retired ID
- Every rule must have at least one passing and one failing test fixture in `testdata/`
- `severity: critical` rules require Security Agent review before merge
- MITRE ATT&CK mapping required for `network`, `tls`, `protocols` categories
- Rules are append-only in a release — never modify a published rule ID's `condition` (create a new version instead)
