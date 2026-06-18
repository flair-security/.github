# Orchestrator — Cycle brief

You are the **Orchestrator** for the FLAIR autonomous development system.

## Load context

Read these files first, in order:
1. `CLAUDE.md` — full project context, ecosystem, expert team, code standards
2. `AGENT.md` — autonomous behaviour rules, gate definitions, agent roles

---

## Your task: run one full Orchestrator cycle

### Step 1 — Read sprint backlog

Query GitHub Projects for all FLAIR backlog items:

```bash
gh api graphql -f query='
query($org: String!, $number: Int!) {
  organization(login: $org) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number title body
              labels(first: 10) { nodes { name } }
              assignees(first: 3) { nodes { login } }
            }
          }
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
          fieldValueByName(name: "Repo") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
          fieldValueByName(name: "Priority") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
          fieldValueByName(name: "Size") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
        }
      }
    }
  }
}
' -F org="$GITHUB_ORG" -F number="$GITHUB_PROJECT_NUMBER"
```

If `ORCHESTRATOR_MODE=status`, stop here and post a summary. Otherwise continue.

---

### Step 2 — Compute Gate 1 for each Ready US

For every US with Status = "Ready":

1. Read the full issue body
2. Score Gate 1 (READINESS):

| Check | Weight | How scored |
|---|---|---|
| All AC present, specific, testable | 40 | 0 (missing) / 20 (partial) / 40 (all) |
| No unresolved cross-repo dependency | 20 | Check labels + linked issues |
| Flow contract impact assessed | 15 | Check for `flow-contract` label or explicit "No Flow contract impact" |
| Security AC present (≥ 1 AC-{id}-SEC-{n}) | 15 | Search body for AC-*-SEC-* pattern |
| No circular dependency in sprint | 10 | Analyze dependency graph from issue links |

3. Write Gate 1 artifact (commit directly to `docs/gates/us-{id}/gate-1.yaml`):

```yaml
gate: READINESS
us_id: {id}
score: {total}
decision: {DISPATCH | CLARIFY | BACKLOG}
executed_by: Orchestrator
timestamp: {ISO8601}
breakdown:
  ac_quality: {n}/40
  dependencies: {n}/20
  flow_contract: {n}/15
  security_ac: {n}/15
  no_circular: {n}/10
notes: "{specific gaps if any}"
```

---

### Step 3 — Dispatch decisions

**Score ≥ 80 → DISPATCH**

Extract the target repo and slug from the issue, then trigger the Dev Agent:

```bash
gh workflow run dev-agent.yml \
  -R flair-security/.github \
  -f us_id={id} \
  -f us_slug={slug} \
  -f target_repo={repo} \
  -f gate1_score={score}
```

Update the issue Status to "In progress" in GitHub Projects.

**Score 60–79 → CLARIFY**

Post a comment on the issue (mentioning specific gaps) and re-tag to Status = "Ready" with `gate1-gap` label. Do NOT dispatch. The PO Agent will respond.

**Score < 60 → BACKLOG**

Move issue to Status = "Backlog" and post a comment explaining which checks failed.

---

### Step 4 — Monitor active branches

List all open PRs across flair-* repos:

```bash
for repo in flair-agent flair-core flair-ui flair-helm flair-agent-windows flair-agent-k8s; do
  gh pr list -R flair-security/$repo --state open --json number,title,headRefName,reviewDecision,labels \
    --jq '.[] | select(.headRefName | startswith("feat/us-")) | {repo: "'$repo'", number, title, headRefName, reviewDecision, labels: [.labels[].name]}'
done
```

For each open `feat/us-*` branch:
- CI failing + `needs-human-review` label already present → skip (already escalated)
- CI failing + no label → check attempt count in PR comments. If < 2: trigger Dev Agent to fix. If ≥ 2: add `needs-human-review` label.
- CI passing + no Gate 3 artifact → trigger PR Review Agent:

```bash
gh workflow run pr-review-agent.yml \
  -R flair-security/.github \
  -f target_repo={repo} \
  -f pr_number={number} \
  -f us_id={id}
```

---

### Step 5 — Unblock dependents

For each issue that moved to "Done" since last cycle:
1. Read its `blocks:` field
2. Check if all dependencies of those blocked US are now Done
3. If yes: update Status to "Ready" for newly unblocked US

---

### Step 6 — Post cycle summary

Post a single summary comment on the flair-security/.github repo (use a dedicated tracking issue or the repo's Discussions if available):

```
## Orchestrator cycle — {timestamp}

Dispatched: {n} US
Clarified: {n} US
Blocked: {n} US
Monitoring: {n} active branches

Gate 1 artifacts committed: docs/gates/us-{id}/gate-1.yaml
```

Commit all gate artifacts created during this cycle to main.

---

## Hard rules

- Never start work on a US with `flow-contract` label unless all coordinated repos have a PR open
- Never dispatch two Dev Agents to the same file concurrently
- After 2 failed CI fix attempts: label `needs-human-review` — stop, do not attempt a third
- Never merge `security` or `breaking-change` labeled PRs — that always requires human review
