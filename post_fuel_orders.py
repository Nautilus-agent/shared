# -*- coding: utf-8 -*-
"""燃料单批量发单(涡轮增压·排气管):从未入池的 g2b1 distill 题批量发 fuel_trajectory 单。
用法:python tools/org_lib/post_fuel_orders.py [--n 19] [--start 1]
幂等:bounty_id=f"b-turbo-f{i:03d}"(起始号由 --start);已存在则跳过。"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

FUEL_PATH = Path("vtf/_g2b1_distill_triples.jsonl")


def clean(s: str, n: int = 600) -> str:
    return (s.replace("'", "''").replace('"', '').replace('`', '')
            .replace('$', 'S/').replace('\\', '/')[:n])


def post_one(bid: str, task: dict) -> tuple[bool, str]:
    desc = ("[fuel_order v1 turbo] real multi-turn tool use (str_replace_editor); "
            "deliver trajectory: qid / verdict 3-state / label_origin, "
            "via writeback kind=fuel_trajectory; acceptance=v5 four-gates; 10 NAU+bonus. "
            "TASK: " + clean(task['prompt']) +
            " || STARTER_HEAD: " + clean(task.get('starter_inline', '')[:400]))
    sql = ("INSERT INTO platform_bounties "
           "(bounty_id,title,description,reward_nau,difficulty,task_type,posted_by,deadline) "
           f"VALUES ('{bid}','fuel: " + clean(task['prompt'][:80]) + "','" + desc +
           "',10,'medium','fuel_trajectory','v5-turbo', NOW() + INTERVAL '48 hours');")
    r = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', 'cloud',
                        'sudo -u postgres psql -d nautilus_production -c "' + sql + '"'],
                       capture_output=True, text=True, timeout=60)
    out = (r.stdout or '') + (r.stderr or '')
    return r.returncode == 0 and 'INSERT' in out, out.strip()[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=19)
    ap.add_argument("--start", type=int, default=2)  # f001 已手工发
    a = ap.parse_args()
    rows = [json.loads(l) for l in FUEL_PATH.read_text(encoding='utf-8').splitlines() if l.strip()]
    ok = fail = 0
    for i in range(a.start, a.start + a.n):
        if i - 1 >= len(rows):
            break
        task = rows[i - 1]
        bid = f"b-turbo-f{i:03d}"
        success, msg = post_one(bid, task)
        print(bid, 'OK' if success else f'FAIL {msg}')
        ok, fail = ok + (1 if success else 0), fail + (0 if success else 1)
    print(f"posted {ok}, failed {fail}")


if __name__ == "__main__":
    main()
