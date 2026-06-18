# Pull Request

## Linked User Story

<!-- Required — link to the story file and GitHub issue -->
- Story file: `flair-docs/stories/us-{id}.md`
- Issue: #{issue_id}
- Branch: `feat/us-{id}-{slug}`

---

## Summary

<!-- What does this PR implement? One paragraph maximum. -->

---

## AC coverage

<!-- List every AC from the story file and the test that covers it.
     An AC without a test = incomplete implementation. -->

| AC ID | Description | Test | Status |
|---|---|---|---|
| AC-{id}-01 | ... | `TestXxx_AC{id}_01_...` | ✅ / ⬜ |
| AC-{id}-SEC-01 | ... | `TestXxx_AC{id}_SEC01_...` | ✅ / ⬜ |

---

## Gate artifacts

<!-- Confirm gate artifacts are committed in docs/gates/us-{id}/ -->

- [ ] Gate 1 — Readiness: `docs/gates/us-{id}/gate-1.yaml` — score: ___
- [ ] Gate 2 — Coverage (latest): `docs/gates/us-{id}/gate-2-{sha}.yaml` — score: ___
- [ ] Gate 3 — Quality: `docs/gates/us-{id}/gate-3.yaml` — score: ___

---

## Flow contract impact

- [ ] This PR modifies the `Flow` struct → coordinated PRs opened and linked
- [ ] This PR adds a new `Metadata` key: `___` — documented in `docs/ARCHITECTURE.md`
- [ ] No `Flow` contract impact

---

## Security

- [ ] No `--tls-verify=false` or equivalent introduced
- [ ] No secrets, tokens, certificates or private keys in diff
- [ ] Security ACs (AC-{id}-SEC-*) all covered by tests
- [ ] TruffleHog scan clean (confirmed by CI)
- [ ] NOSONAR / nosemgrep annotations include justification

---

## Checklist

- [ ] Rebased on latest `main` — no merge commits
- [ ] Commits are human-readable — no `wip`, `fix again`, `test` commits
- [ ] `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` on AI-assisted commits
- [ ] GoDoc / TSDoc on all new exported symbols

---

## Notes for reviewer

<!-- Anything the reviewer should pay particular attention to.
     Known tradeoffs, deferred work, or design decisions not obvious from the diff. -->
