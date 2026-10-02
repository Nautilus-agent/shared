# -*- coding: utf-8 -*-
"""主脑入遥测(2026-10-01·消最大盲区):boot.log 增量→组件计数→agent_tool_calls 汇总行。
旁路设计:零侵入(不改主脑/不重启);水位文件防重防丢;写表走 ssh cloud psql(15432 隧道源头)。
组件映射:dispatch_mixin→brain:dispatch · daemon cycle/heartbeat→brain:daemon_cycle
        · llm_client→brain:llm_call · telegram→brain:tg_poll · notifier push→brain:notify_push
用法:python tools/org_lib/brain_telemetry.py [--log vtf/_v5brain_boot.log]
调度:schtasks NautilusV5-BrainTelemetry 每 10min(安装脚本见文末注释)。
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

AGENT_ID = "ag_local_main"
LOG = Path("vtf/_v5brain_boot.log")
WM = Path("vtf/_brain_tel.offset")

_PATTERNS = [
    ("brain:dispatch", re.compile(r"INFO nautilus_v5\.runtime\.dispatch_mixin")),
    ("brain:llm_call", re.compile(r"INFO nautilus_v5\.llm_client")),
    ("brain:tg_poll", re.compile(r"INFO httpx · HTTP Request: POST https://api\.telegram\.org")),
    ("brain:notify_push", re.compile(r"(INFO|WARNING) nautilus_v5\.notifier")),
]
_CYCLE = re.compile(r"INFO nautilus_v5\.daemon · (cycle|heartbeat)")


def parse_components(lines: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for l in lines:
        for name, pat in _PATTERNS:
            if pat.search(l):
                out[name] = out.get(name, 0) + 1
                break
        else:
            if _CYCLE.search(l):
                out["brain:daemon_cycle"] = out.get("brain:daemon_cycle", 0) + 1
    return out


def build_rows(counts: dict[str, int], window: tuple[str, str]) -> list[dict]:
    w0, w1 = window
    return [{"agent_id": AGENT_ID, "tool_name": k, "args_summary": f"window={w0}..{w1}",
             "output_summary": f"count={v}", "success": True, "elapsed_ms": 0, "ts": w1,
             "phase": "telemetry_rollup"}
            for k, v in sorted(counts.items())]


def watermark_io(path: Path, read_default: int = -1, write: int | None = None) -> int:
    if write is not None:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(str(write), encoding="utf-8")
        tmp.replace(path)
        return write
    if path.exists():
        try:
            return int(path.read_text(encoding="utf-8").strip() or read_default)
        except ValueError:
            return read_default
    return read_default


def _sql_escape(s: str) -> str:
    return s.replace("'", "''")


def insert_sql(rows: list[dict]) -> str:
    vals = ", ".join(
        f"('{_sql_escape(r['agent_id'])}','{_sql_escape(r['tool_name'])}',"
        f"'{_sql_escape(r['args_summary'])}','{_sql_escape(r['output_summary'])}',"
        f"true,0,'{r['ts']}','{r['phase']}')" for r in rows)
    return ("INSERT INTO agent_tool_calls (agent_id,tool_name,args_summary,output_summary,"
            f"success,elapsed_ms,ts,phase) VALUES {vals};")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(LOG))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    log = Path(a.log)
    size = log.stat().st_size
    off = watermark_io(WM)
    if off < 0:
        watermark_io(WM, write=size)
        print(f"首跑:水位置 {size}(只记新增,不回填历史)")
        return
    with log.open("rb") as f:
        f.seek(off)
        chunk = f.read(size - off).decode("utf-8", "replace")
    lines = [l for l in chunk.splitlines() if l.startswith("2026-")]
    if not lines:
        print("无新日志行")
        watermark_io(WM, write=size)
        return
    counts = parse_components(lines)
    window = (lines[0][:19], lines[-1][:19])
    rows = build_rows(counts, window)
    if not rows:
        print(f"窗口 {window[0]}..{window[1]}:无匹配组件行")
        watermark_io(WM, write=size)
        return
    sql = insert_sql(rows)
    if a.dry_run:
        print(sql[:400])
    else:
        import subprocess
        cmd = ["ssh", "-o", "ConnectTimeout=15", "cloud",
               f'sudo -u postgres psql -d nautilus_production -c "{sql.replace(chr(34), chr(39))}"']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        ok = "INSERT" in r.stdout
        print(("写入 " if ok else "失败 ") + f"{len(rows)} 行;stdout={r.stdout.strip()[:60]};"
              f"stderr={r.stderr.strip()[:80]}")
    watermark_io(WM, write=size)


if __name__ == "__main__":
    main()
