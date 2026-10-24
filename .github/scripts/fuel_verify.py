#!/usr/bin/env python3
"""Fuel trajectory gate — fail-closed (阶段B). Kairos.

旧版(yaml 内联)是 fail-open: trajectories/ 下 0 个 *.json 时 exit 0,
于是「门」永远绿、覆盖率永远 0 —— 真空通过 (vacuous pass)。

本版规则:
  gate  模式(PR/push 改 trajectories/** 时): 0 个 *.json → exit 1
  report 模式(定时/dispatch): 只报覆盖率, 永远 exit 0, 覆盖率 0 写 warning+summary
  字段门: qid / verdict / trajectory 必填; label_origin 必填且 != 'LLM'
  递归 rglob, 与 paths 过滤对齐
"""
import json, os, pathlib, sys

REQUIRED = ("qid", "verdict", "trajectory")
MODE = os.environ.get("MODE", "gate").strip().lower()
DIR = pathlib.Path(os.environ.get("TRAJ_DIR", "trajectories"))


def check_file(p):
    errs = []
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        return [f"invalid json: {e}"]
    if not isinstance(d, dict):
        return ["not a json object"]
    for k in REQUIRED:
        if k not in d:
            errs.append(f"missing {k}")
    if "label_origin" not in d:
        errs.append("missing label_origin")
    elif d.get("label_origin") == "LLM":
        errs.append("label_origin == 'LLM' (LLM self-report not allowed)")
    return errs


def emit(line):
    print(line)


def summary(line):
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(line + "\n")


def main():
    files = sorted(DIR.rglob("*.json")) if DIR.exists() else []
    ok = bad = 0
    for f in files:
        errs = check_file(f)
        if errs:
            bad += 1
            emit(f"  BAD {f}: {'; '.join(errs)}")
        else:
            ok += 1
            emit(f"  OK  {f}")
    cov = f"scanned={len(files)} valid={ok} bad={bad}"
    emit(f"fuel-verify mode={MODE} {cov}")
    if len(files) == 0:
        summary(f"### Fuel coverage = 0%\n\n`{DIR}` 下 0 个 *.json — 门没有校验任何轨迹。")
        emit(f"::warning::COVERAGE=0 — {DIR} 下 0 个 *.json,本轮未校验任何轨迹")
        if MODE == "gate":
            emit("FATAL: 0 个轨迹文件 → fail-closed(阶段B), 不许真空通过")
            return 1
        return 0
    summary(f"### Fuel coverage\n\n`{cov}`")
    if bad:
        emit(f"FATAL: {bad} 个轨迹未过字段门")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
