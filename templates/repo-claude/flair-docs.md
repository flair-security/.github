# CLAUDE.md — flair-docs

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: MkDocs Material, Markdown, Python  
**Role**: Documentation site — architecture, user guide, API reference, regulatory mapping, US stories  
**Licence**: CC-BY-4.0

---

## Build & test commands

```bash
# Install
pip install -r requirements.txt

# Dev server
mkdocs serve

# Production build
mkdocs build --strict

# Lint markdown
markdownlint docs/

# Check broken links
mkdocs build 2>&1 | grep WARNING
```

---

## Repo structure

```
flair-docs/
  docs/
    index.md             ← home page
    architecture/        ← system design, ADRs
    user-guide/          ← operator and RSSI guides
    api-reference/       ← auto-generated from OpenAPI
    regulatory/          ← NIS2 / DORA / GDPR mapping tables
    stories/             ← US story files (us-{id}.md)
  overrides/             ← MkDocs Material overrides
  mkdocs.yml             ← site config
```

---

## Story files

US story files live at `docs/stories/us-{id}.md`. They follow `.project/us-template.md` format.
The Dev Agent populates the Test Mapping table when implementing the US.
Never delete a story file — they are the audit trail.

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-ac-traceability | all US |
| 1 (always) | skill-bdd-architecture | US story changes |

---

## Repo-specific rules

- Regulatory mapping tables (NIS2/DORA/GDPR) must be reviewed by Security Agent before merge
- `docs/stories/` is write-once append — no retroactive AC edits after a US is Done
- API reference is auto-generated — do not manually edit files in `docs/api-reference/`
