# LAUNCH.md — Mode autonome FLAIR depuis l'IDE

> Tous les agents tournent **localement** depuis l'IDE ou terminal.
> GitHub Actions = CI + triage backlog uniquement. Claude ne tourne jamais sur un runner.
> Lire `AGENT.md` pour le comportement des agents. `CLAUDE.md` pour le contexte projet.

---

## Prérequis

```bash
# Claude Code CLI (déjà installé si tu utilises l'extension VS Code)
npm install -g @anthropic-ai/claude-code

# Authentification Claude Code via claude.ai (Pro Max — pas d'API key nécessaire)
claude auth status   # vérifie que tu es loggé

# GitHub CLI + token (scope: project, repo, issues, read:org)
export GH_TOKEN=github_pat_...
gh auth login --with-token <<< "$GH_TOKEN"

# Python
pip install pyyaml requests
```

**Repos clonés côte à côte :**

```
parent/
  flair-security/.github/   ← ce repo
  flair-agent/
  flair-core/
  flair-ui/
  ...
```

---

## Cycle Orchestrateur

```bash
# Depuis flair-security/.github/
claude --headless \
  --print "$(cat .project/prompts/orchestrator.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

Depuis **VS Code** : ouvrir Claude Code → coller le contenu de `.project/prompts/orchestrator.md`.

---

## Dev Agent sur un US

```bash
# 1. Assembler le contexte (CLAUDE.md + AGENT.md + skills ciblés + brief Dev Agent)
python3 scripts/build-agent-context.py \
  --us 42 \
  --repo flair-agent \
  --output /tmp/context-us42.md

# 2. Se placer sur la branche (créée par le scaffold dev-agent.yml ou manuellement)
cd ../flair-agent
git fetch origin
git checkout feat/us-42-grpc-detection

# 3. Lancer
claude --headless \
  --print "$(cat /tmp/context-us42.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

---

## Autres agents

```bash
# PO Agent
cd flair-security/.github
claude --headless \
  --print "$(cat .project/prompts/po-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# Architect Agent (passer le body de l'issue en contexte)
claude --headless \
  --print "$(gh issue view 42 --repo flair-security/flair-core --json body -q .body)

$(cat .project/prompts/architect-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# Security Agent
claude --headless \
  --print "$(gh issue view 42 --repo flair-security/flair-core --json body -q .body)

$(cat .project/prompts/security-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# PR Review Agent
cd ../flair-core
claude --headless \
  --print "PR_NUMBER=42
TARGET_REPO=flair-core

$(cat ../flair-security/.github/.project/prompts/pr-review-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

---

## Vérifier le backlog

```bash
python3 scripts/check-backlog.py                        # tout
python3 scripts/check-backlog.py --status Ready         # prêts
python3 scripts/check-backlog.py --repo flair-core      # par repo
python3 scripts/check-backlog.py --format json          # JSON
```

---

## Rôle des GitHub Actions

| Workflow | Ce qu'il fait |
|---|---|
| `validate.yml` | Lint YAML + skills à chaque push |
| `auto-label.yml` | Labels automatiques sur issues/PRs |
| `scorecard.yml` | OpenSSF Scorecard hebdomadaire |
| `stale.yml` | Nettoyage issues/PRs stagnantes |

Tous les agents (Orchestrateur, Dev, PO, Architect, Security, QA, PR Review) tournent **depuis l'IDE uniquement**.

---

## Initialiser un repo composant

```bash
REPO=flair-core

gh repo create flair-security/$REPO --private
gh repo clone flair-security/$REPO ../$REPO

cp templates/repo-claude/$REPO.md ../$REPO/CLAUDE.md
mkdir -p ../$REPO/.claude
cp templates/repo-settings/$REPO.json ../$REPO/.claude/settings.json 2>/dev/null || \
  cp templates/repo-settings/base.json ../$REPO/.claude/settings.json

cd ../$REPO
git add CLAUDE.md .claude/settings.json
git commit -m "chore: add Claude Code context and safety settings

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin main
```

---

## Secrets GitHub (CI uniquement)

| Secret | Scope | Usage |
|---|---|---|
| `GH_TOKEN_PROJECTS` | `project`, `read:org` | `check-backlog.py` dans orchestrator.yml |
| `GH_TOKEN_REPOS` | `repo` | Création branches dans dev-agent.yml |

Claude Code s'authentifie via `claude auth` (abonnement claude.ai) — pas d'`ANTHROPIC_API_KEY` nécessaire.

---

## Premier démarrage

- [ ] `ANTHROPIC_API_KEY` exportée localement
- [ ] `gh auth login` OK
- [ ] GitHub Project n°1 créé avec champs Status / Priority / Repo / Phase / Size
- [ ] Repos MVP bootstrappés (flair-agent, flair-core, flair-ui)
- [ ] Premier Epic + une US avec Status=Ready dans le Project
- [ ] Premier cycle Orchestrateur lancé depuis l'IDE
