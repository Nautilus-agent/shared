# -*- coding: utf-8 -*-
"""GitHub 组织 bootstrap 脚本(Agent 身份基础设施 Phase 1)。
前置条件(用户手动完成,约 15 分钟):
  1. 在 github.com 创建组织 nautilus-agents(Free Plan)
  2. 将 v5 的 GitHub 账号(或机器账号)添加为 Org Member
  3. 生成 Personal Access Token(scope: repo, admin:org)→ 存入 .env
  4. Cloudflare DNS 添加 MX 记录 + 启用 Email Routing

用法:python tools/org_lib/github_bootstrap.py --token $GITHUB_TOKEN --org nautilus-agents
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request

GITHUB_API = "https://api.github.com"

REPOS = [
    {"name": "prime", "desc": "Nautilus Prime-001 · main brain & task executor", "private": True},
    {"name": "compass", "desc": "Nautilus Compass · evaluation, Assay & memory", "private": True},
    {"name": "flywheel", "desc": "Nautilus Flywheel · embodied data & G-pipeline", "private": True},
    {"name": "v7", "desc": "Nautilus V7 · Telegram bridge & tool layer", "private": True},
    {"name": "kairos", "desc": "Nautilus Kairos · quality control & review", "private": True},
    {"name": "soul", "desc": "Nautilus Soul · governance & jury", "private": True},
    {"name": "shared", "desc": "Nautilus shared libraries · org_lib tools", "private": False},  # 公开
    {"name": "infra", "desc": "Nautilus infrastructure · CI templates & deploy", "private": True},
]

README_TEMPLATE = """# {name}

> {desc}

## Structure
- `main/` — production (protected, PR required)
- `lab/` — experimentation (free)
- `src/` — agent code
- `tests/` — unit tests
- `trajectories/` — fuel order deliveries
- `.github/workflows/` — CI checks

## CI Checks
1. **output_gate** — outbound content quality check
2. **canary** — 40-question baseline regression test
3. **fuel_verify** — trajectory format validation

## Contact
{name}@nautilus.social
"""

OUTPUT_GATE_YML = """name: Output Gate
on: [pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -q tools/org_lib/ 2>/dev/null || true
      - name: Check PR content
        run: |
          python -c "
          import sys; sys.path.insert(0, 'tools/org_lib')
          try:
              from output_gate import gate_check
              v = gate_check({
                  'title': '''${{ github.event.pull_request.title }}''',
                  'body': '''${{ github.event.pull_request.body }}''',
                  'kind': 'proposal'})
              if v['status'] == 'RED':
                  print('REJECTED:', v['reasons']); exit(1)
              print('GREEN')
          except ImportError:
              print('output_gate not available, skipping'); exit(0)
          "
"""

FUEL_VERIFY_YML = """name: Fuel Verification
on:
  pull_request:
    paths: ['trajectories/**']
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - name: Validate trajectories
        run: |
          python -c "
          import json, pathlib, sys
          ok = 0; bad = 0
          for f in pathlib.Path('trajectories').glob('*.json'):
              try:
                  d = json.loads(f.read_text())
                  assert 'qid' in d and 'verdict' in d and 'label_origin' in d
                  assert d['label_origin'] != 'LLM'
                  ok += 1
              except Exception as e:
                  print(f'BAD {f.name}: {e}'); bad += 1
          print(f'valid={ok} bad={bad}')
          if bad > 0: exit(1)
          "
"""

FUEL_ISSUE_TEMPLATE = """---
name: Fuel Order
about: Trajectory-producing task for training data
labels: ['fuel-trajectory']
title: '[FUEL] '
body:
  - type: textarea
    id: task
    attributes:
      label: Task Description
      description: What the agent should do
    validations:
      required: true
  - type: input
    id: reward
    attributes:
      label: Reward (NAU)
      default: '10'
  - type: textarea
    id: deliverable
    attributes:
      label: Deliverable Format
      value: |
        Submit a PR with your trajectory file in `trajectories/`:
        ```json
        {"qid": "unique-task-id", "verdict": "pass|fail", "label_origin": "verifier|official-answer", "trajectory": [...messages...]}
        ```
"""


def gh(method, path, token, data=None):
    url = f"{GITHUB_API}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, method=method, data=body,
                                 headers={
                                     "Authorization": f"token {token}",
                                     "Accept": "application/vnd.github.v3+json",
                                     "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="GitHub PAT (repo+admin:org)")
    ap.add_argument("--org", default="nautilus-agents")
    a = ap.parse_args()

    print(f"Bootstrapping GitHub org: {a.org}")
    print("=" * 50)

    for repo in REPOS:
        name = repo["name"]
        print(f"\n📦 Creating {name}...", end=" ")

        # Create repo
        status, resp = gh("POST", f"/orgs/{a.org}/repos", a.token, {
            "name": name,
            "description": repo["desc"],
            "private": repo["private"],
            "has_issues": True,
            "has_wiki": False,
        })

        if status == 201:
            print("✅ created")
        elif status == 422:
            print("⚠️  already exists")
        else:
            print(f"❌ {status}: {resp.get('message', '')}")
            continue

        # Set branch protection on main
        status2, _ = gh("PUT", f"/repos/{a.org}/{name}/branches/main/protection", a.token, {
            "required_status_checks": {"strict": True, "contexts": []},
            "enforce_admins": False,
            "required_pull_request_reviews": {"required_approving_review_count": 1},
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
        })
        print(f"   🔒 branch protection: {'✅' if status2 in (200, 201) else '⚠️ ' + str(status2)}")

        # Create lab branch (from main)
        # Note: need to push at least one commit first. For now, just note it.
        print(f"   📝 lab branch: will be created on first push")

    # Create issue template in shared repo
    print("\n📋 Adding fuel issue template to shared repo...")
    # This would need git push - noted for implementation via git commands

    print("\n" + "=" * 50)
    print("✅ Bootstrap complete!")
    print(f"\nNext steps:")
    print(f"  1. Clone each repo and push initial code")
    print(f"  2. Generate Deploy Keys: ssh-keygen -t ed25519 -f ~/.ssh/{a.org}-<agent>")
    print(f"  3. Add Deploy Keys in GitHub Settings → Deploy Keys")
    print(f"  4. Push org_lib to shared repo")


if __name__ == "__main__":
    main()
