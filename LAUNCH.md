# LAUNCH.md — Démarrer le mode autonome FLAIR

> Ce fichier est le point d'entrée unique pour opérateurs humains.
> Lire `AGENT.md` pour comprendre le comportement des agents.
> Lire `CLAUDE.md` pour le contexte projet complet.

---

## Prérequis

### Secrets GitHub à configurer (Settings → Secrets → Actions)

| Secret | Scope requis | Usage |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Invocation Claude Code |
| `GH_TOKEN_PROJECTS` | `project`, `repo`, `issues` | Orchestrateur — lecture/écriture GitHub Projects |
| `GH_TOKEN_REPOS` | `repo`, `pull-requests`, `issues` | Dev Agent — travail dans les repos composants |

### Localement

```bash
# CLI
npm install -g @anthropic-ai/claude-code

# Variables
export ANTHROPIC_API_KEY=sk-ant-...
export GH_TOKEN=<github_token_with_projects_scope>
gh auth login  # pour les scripts Python
```

### Repos clonés côte à côte

```
parent/
  flair-security/.github/   ← ce repo
  flair-agent/
  flair-core/
  flair-ui/
  ...
```

---

## Lancement du cycle autonome complet

### Option A — GitHub Actions (production, recommandé)

```bash
# Déclencher manuellement un cycle Orchestrateur
gh workflow run orchestrator.yml \
  --repo flair-security/.github \
  -f mode=full

# Suivre l'exécution
gh run watch --repo flair-security/.github
```

Le cron est déjà configuré toutes les 6 heures.

### Option B — Local (debug / développement)

```bash
# Depuis flair-security/.github/
claude --headless \
  --print "$(cat .project/prompts/orchestrator.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

---

## Lancer un agent spécifique sur un US

### Dispatcher manuellement le Dev Agent sur un US

```bash
# Via GitHub Actions (recommandé — utilise les secrets centralisés)
gh workflow run dev-agent.yml \
  --repo flair-security/.github \
  -f us_id=42 \
  -f us_slug=grpc-detection \
  -f target_repo=flair-agent \
  -f gate1_score=87

# Suivre le travail du Dev Agent
gh run watch --repo flair-security/.github
```

### Localement dans un repo composant

```bash
# Construire le contexte avec injection de skills
python3 scripts/build-agent-context.py \
  --us 42 \
  --repo flair-agent \
  --output /tmp/context-us42.md

# Lancer le Dev Agent
cd ../flair-agent
claude --headless \
  --print "$(cat /tmp/context-us42.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

---

## Lancer chaque agent manuellement

```bash
# PO Agent — générer ou affiner les US d'un Epic
claude --headless \
  --print "$(cat .project/prompts/po-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# Architect Agent — review technique d'un US
claude --headless \
  --print "EPIC_OR_US_CONTEXT: $(gh issue view 42 --json body -q .body)\n\n$(cat .project/prompts/architect-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# Security Agent — challenge AC sécurité
claude --headless \
  --print "US_CONTEXT: $(gh issue view 42 --json body -q .body)\n\n$(cat .project/prompts/security-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"

# PR Review Agent — gate 3 + gate 4 sur une PR ouverte
cd ../flair-core
claude --headless \
  --print "PR_NUMBER: 42\nREPO: flair-core\n\n$(cat ../flair-security/.github/.project/prompts/pr-review-agent.md)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep"
```

---

## Vérifier l'état du backlog

```bash
# Rapport backlog complet
python3 scripts/check-backlog.py --org flair-security --project 1

# Filtrer par status
python3 scripts/check-backlog.py --status Ready
python3 scripts/check-backlog.py --status "In progress"

# Export JSON
python3 scripts/check-backlog.py --format json > /tmp/backlog.json
```

---

## Initialiser un nouveau repo composant

```bash
# Copier le template CLAUDE.md vers le nouveau repo
cp templates/repo-claude/flair-agent.md ../flair-agent/CLAUDE.md

# Copier le settings.json approprié
mkdir -p ../flair-agent/.claude
cp templates/repo-settings/flair-agent.json ../flair-agent/.claude/settings.json

# Committer
cd ../flair-agent
git add CLAUDE.md .claude/settings.json
git commit -m "chore: add Claude Code context and safety settings"
```

---

## Premier démarrage — checklist

- [ ] Secrets GitHub configurés (`ANTHROPIC_API_KEY`, `GH_TOKEN_PROJECTS`, `GH_TOKEN_REPOS`)
- [ ] GitHub Project n°1 créé dans l'org flair-security avec les champs Status, Priority, Repo, Phase, Size
- [ ] Au moins un Epic + une US avec Status=Ready dans GitHub Projects
- [ ] Tous les repos composants ont leur `CLAUDE.md` et `.claude/settings.json` (voir `templates/`)
- [ ] `gh auth login` effectué localement
- [ ] Premier cycle Orchestrateur déclenché manuellement et validé

---

## Interventions humaines attendues

| Déclencheur | Action humaine |
|---|---|
| PR labelée `needs-human-review` | Lire le gate artifact + décider du merge |
| PR labelée `breaking-change` + `flow-contract` | Valider les coordinated PRs cross-repo |
| Gate 4 score < 60 | Lire le rapport d'agent + débloquer ou rediriger |
| Orchestrateur bloqué après 2 tentatives | Lire `needs-human-review` label + résoudre le blocage |
| Nouveau Epic ou pivot stratégique | Alimenter GitHub Projects manuellement ou via PO Agent |
