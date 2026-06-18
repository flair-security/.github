#!/usr/bin/env python3
"""Build Dev Agent context for a FLAIR User Story.

Assembles: org CLAUDE.md + repo CLAUDE.md + AGENT.md + US issue + relevant skills + dev-agent prompt.
Outputs a single markdown file ready to be passed to `claude --print`.

Usage:
  python3 scripts/build-agent-context.py \\
    --us 42 \\
    --repo flair-core \\
    --gate1-score 87 \\
    --output /tmp/agent-context.md
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # noqa: F401 — imported for future skill metadata parsing
except ImportError:
    pass  # pyyaml optional — only needed for advanced load_when evaluation


def gh_issue(org: str, repo: str, number: int) -> dict:
    result = subprocess.run(
        ['gh', 'issue', 'view', str(number),
         '--repo', f'{org}/{repo}',
         '--json', 'number,title,body,labels,assignees'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Warning: gh issue fetch failed: {result.stderr.strip()}", file=sys.stderr)
        return {'number': number, 'title': f'US-{number}', 'body': '', 'labels': [], 'assignees': []}
    return json.loads(result.stdout)


# Skills always loaded per target repo
REPO_BASE_SKILLS: dict[str, list[str]] = {
    'flair-agent':           ['skill-solid-go', 'skill-error-handling', 'skill-ac-traceability', 'skill-observability', 'skill-ebpf-architecture'],
    'flair-agent-windows':   ['skill-solid-go', 'skill-error-handling', 'skill-ac-traceability', 'skill-observability'],
    'flair-agent-k8s':       ['skill-solid-go', 'skill-error-handling', 'skill-ac-traceability', 'skill-observability', 'skill-ebpf-architecture'],
    'flair-core':            ['skill-solid-go', 'skill-go-service-layer', 'skill-error-handling', 'skill-ac-traceability', 'skill-bdd-architecture', 'skill-observability'],
    'flair-ui':              ['skill-ac-traceability', 'skill-angular-security'],
    'flair-helm':            ['skill-devops-cicd', 'skill-ac-traceability'],
    'flair-docs':            ['skill-ac-traceability', 'skill-bdd-architecture'],
    'flair-terraform-aws':   ['skill-devops-cicd', 'skill-ac-traceability'],
    'flair-terraform-azure': ['skill-devops-cicd', 'skill-ac-traceability'],
    'flair-terraform-gcp':   ['skill-devops-cicd', 'skill-ac-traceability'],
    'flair-sdk-go':          ['skill-solid-go', 'skill-error-handling', 'skill-api-design', 'skill-ac-traceability'],
    'flair-sdk-python':      ['skill-api-design', 'skill-ac-traceability'],
    'flair-rules':           ['skill-ac-traceability'],
}

# Keyword → conditional skill (checked against issue body + labels)
KEYWORD_SKILLS: list[tuple[list[str], str]] = [
    (['auth', 'jwt', 'oidc', 'mtls', 'token', 'enrollment', 'certificate'],   'skill-authentication'),
    (['score', 'scoring', 'alert', 'detection', 'rule', 'threshold', 'mitre'], 'skill-security-scoring'),
    (['docker', 'container', 'kubernetes', 'k8s', 'deploy', 'pipeline', 'ci'], 'skill-devops-cicd'),
    (['performance', 'benchmark', 'throughput', 'latency', 'memory', 'cpu'],   'skill-performance'),
    (['api', 'rest', 'http', 'endpoint', 'grpc', 'openapi', 'swagger'],        'skill-api-design'),
    (['test', 'coverage', 'unit', 'integration', 'e2e', 'playwright'],         'skill-testing-strategy'),
    (['angular', 'typescript', 'frontend', 'ui', 'component', 'directive'],   'skill-angular-security'),
]


def select_skills(repo: str, body: str, labels: list[str]) -> list[str]:
    skills = list(REPO_BASE_SKILLS.get(repo, ['skill-ac-traceability']))
    body_lower = body.lower()
    labels_lower = [la.lower() for la in labels]

    for keywords, skill in KEYWORD_SKILLS:
        if skill not in skills:
            if any(k in body_lower or k in ' '.join(labels_lower) for k in keywords):
                skills.append(skill)

    return list(dict.fromkeys(skills))  # deduplicate, preserve order


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding='utf-8')
    return f"(file not found: {path})\n"


def main() -> None:
    parser = argparse.ArgumentParser(description='Build FLAIR Dev Agent context for a US')
    parser.add_argument('--us', required=True, type=int, help='User Story issue number')
    parser.add_argument('--repo', required=True, help='Target repository (e.g. flair-core)')
    parser.add_argument('--gate1-score', default='0', dest='gate1_score')
    parser.add_argument('--output', default='/tmp/agent-context.md')
    args = parser.parse_args()

    org = os.environ.get('GITHUB_ORG', 'flair-security')
    repo_root = Path(__file__).parent.parent.resolve()  # .github repo root

    print(f"[build-agent-context] US-{args.us} | repo={args.repo} | gate1={args.gate1_score}", file=sys.stderr)

    # 1. Fetch issue
    issue = gh_issue(org, args.repo, args.us)
    labels = [la['name'] for la in issue.get('labels', [])]
    print(f"  Issue: #{issue['number']} — {issue['title']}", file=sys.stderr)

    # 2. Select skills
    skills = select_skills(args.repo, issue.get('body', ''), labels)
    print(f"  Skills ({len(skills)}): {', '.join(skills)}", file=sys.stderr)

    # 3. Assemble context
    skills_dir = repo_root / '.project' / 'skills'
    parts: list[str] = []

    parts.append(f"""# Dev Agent Context — US-{args.us} in {args.repo}

> Generated by scripts/build-agent-context.py
> Gate 1 score carried from Orchestrator: {args.gate1_score}/100
> Target repository: {args.repo}
> US labels: {', '.join(labels) or 'none'}

""")

    # Org CLAUDE.md
    parts.append("---\n\n# ORGANISATION CLAUDE.md\n\n")
    parts.append(read_file(repo_root / 'CLAUDE.md'))
    parts.append("\n\n")

    # Repo-specific CLAUDE.md template
    repo_claude = repo_root / 'templates' / 'repo-claude' / f'{args.repo}.md'
    if repo_claude.exists():
        parts.append(f"---\n\n# REPO CLAUDE.md ({args.repo})\n\n")
        parts.append(read_file(repo_claude))
        parts.append("\n\n")
    else:
        print(f"  Warning: no repo template found at {repo_claude}", file=sys.stderr)

    # AGENT.md
    parts.append("---\n\n# AGENT.md\n\n")
    parts.append(read_file(repo_root / 'AGENT.md'))
    parts.append("\n\n")

    # US story
    parts.append(f"---\n\n# USER STORY US-{args.us}\n\n")
    parts.append(f"**Issue**: #{issue['number']} — {issue['title']}\n")
    parts.append(f"**Repository**: {args.repo}\n")
    parts.append(f"**Labels**: {', '.join(labels) or 'none'}\n\n")
    body = issue.get('body') or '(no body)'
    parts.append(f"**Body**:\n\n{body}\n\n")

    # Skill files
    loaded = 0
    for skill_name in skills:
        skill_file = skills_dir / f'{skill_name}.yaml'
        if skill_file.exists():
            parts.append(f"---\n\n# SKILL: {skill_name}\n\n```yaml\n")
            parts.append(skill_file.read_text(encoding='utf-8'))
            parts.append("```\n\n")
            loaded += 1
        else:
            print(f"  Warning: skill file not found: {skill_file.name}", file=sys.stderr)

    # Dev Agent prompt
    dev_prompt = repo_root / '.project' / 'prompts' / 'dev-agent.md'
    if dev_prompt.exists():
        parts.append("---\n\n")
        parts.append(dev_prompt.read_text(encoding='utf-8'))
    else:
        print(f"  Warning: dev-agent prompt not found at {dev_prompt}", file=sys.stderr)

    # Write output
    content = ''.join(parts)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')

    print(f"  Written: {output_path} ({len(content):,} chars, {loaded}/{len(skills)} skills loaded)", file=sys.stderr)


if __name__ == '__main__':
    main()
