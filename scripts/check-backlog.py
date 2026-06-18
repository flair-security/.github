#!/usr/bin/env python3
"""Query FLAIR GitHub Projects backlog.

Usage:
  python3 scripts/check-backlog.py
  python3 scripts/check-backlog.py --status Ready
  python3 scripts/check-backlog.py --repo flair-core
  python3 scripts/check-backlog.py --format json > backlog.json
  python3 scripts/check-backlog.py --status Ready --format ids
"""

import argparse
import json
import os
import subprocess
import sys

# GraphQL query using aliases for multiple fieldValueByName calls
GQL = r"""
query($org: String!, $number: Int!) {
  organization(login: $org) {
    projectV2(number: $number) {
      title
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number title url
              labels(first: 10) { nodes { name } }
              assignees(first: 3) { nodes { login } }
            }
          }
          status:   fieldValueByName(name: "Status")   { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          priority: fieldValueByName(name: "Priority") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          repo:     fieldValueByName(name: "Repo")     { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          size:     fieldValueByName(name: "Size")     { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          phase:    fieldValueByName(name: "Phase")    { ... on ProjectV2ItemFieldSingleSelectValue { name } }
        }
      }
    }
  }
}
"""

PRIORITY_ORDER = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, '': 4}


def query_project(org: str, number: int) -> list[dict]:
    result = subprocess.run(
        ['gh', 'api', 'graphql',
         '-f', f'query={GQL}',
         '-F', f'org={org}',
         '-F', f'number={number}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api graphql failed:\n{result.stderr.strip()}")

    data = json.loads(result.stdout)
    gql_errors = data.get('errors')
    if gql_errors:
        raise RuntimeError(f"GraphQL errors: {json.dumps(gql_errors, indent=2)}")

    nodes = data['data']['organization']['projectV2']['items']['nodes']
    items = []
    for node in nodes:
        content = node.get('content') or {}
        if not content.get('number'):
            continue
        items.append({
            'number':    content['number'],
            'title':     content.get('title', ''),
            'url':       content.get('url', ''),
            'status':    (node.get('status')   or {}).get('name', ''),
            'priority':  (node.get('priority') or {}).get('name', ''),
            'repo':      (node.get('repo')     or {}).get('name', ''),
            'size':      (node.get('size')     or {}).get('name', ''),
            'phase':     (node.get('phase')    or {}).get('name', ''),
            'labels':    [la['name'] for la in content.get('labels', {}).get('nodes', [])],
            'assignees': [a['login'] for a in content.get('assignees', {}).get('nodes', [])],
        })
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description='FLAIR GitHub Projects backlog query')
    parser.add_argument('--org',     default=os.environ.get('GITHUB_ORG', 'flair-security'))
    parser.add_argument('--project', type=int, default=int(os.environ.get('GITHUB_PROJECT_NUMBER', '1')))
    parser.add_argument('--status',  help='Filter by status: Ready | Backlog | "In progress" | Done')
    parser.add_argument('--repo',    help='Filter by repo name (e.g. flair-core)')
    parser.add_argument('--format',  choices=['table', 'json', 'ids'], default='table')
    args = parser.parse_args()

    try:
        items = query_project(args.org, args.project)
    except (RuntimeError, KeyError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Apply filters
    if args.status:
        items = [i for i in items if i['status'].lower() == args.status.lower()]
    if args.repo:
        items = [i for i in items if i['repo'].lower() == args.repo.lower()]

    # Output
    if args.format == 'json':
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return

    if args.format == 'ids':
        for i in items:
            print(i['number'])
        return

    # Table — sorted by priority then number
    items_sorted = sorted(items, key=lambda x: (PRIORITY_ORDER.get(x['priority'], 4), x['number']))

    print(f"\n{'#':>4}  {'Status':<14}  {'Pri':<8}  {'Repo':<22}  {'Size':<4}  Title")
    print("─" * 105)
    for i in items_sorted:
        title = i['title']
        if len(title) > 52:
            title = title[:51] + '…'
        print(f"{i['number']:>4}  {i['status']:<14}  {i['priority']:<8}  {i['repo']:<22}  {i['size']:<4}  {title}")

    print(f"\n{len(items)} item(s) shown")
    if args.status:
        print(f"  Status filter : {args.status}")
    if args.repo:
        print(f"  Repo filter   : {args.repo}")


if __name__ == '__main__':
    main()
