# -*- coding: utf-8 -*-
"""自停协议 C 件(org 通用·2026-10-02):agent 停必留三件——sentinel 文件+终函+重启路径。
背景:soul 熔断自停但函件 SLA 全停无人知案(9/24)的通用化。
用法(任何长驻组件停机前调用):
    from org_lib.stop_protocol import graceful_stop
    graceful_stop(name='my-worker', reason='熔断 5 连败',
                  restart='/root/start.sh', sentinel='/var/run/my.pause')
判活方:check_sentinel() 返回 (stopped, meta)。
"""
from __future__ import annotations

import json
import time
from pathlib import Path


def graceful_stop(name: str, reason: str, restart: str, sentinel: str,
                  notify=None) -> dict:
    """三件套:sentinel 落盘 + 终函(可选回调) + 重启路径写入。返回 meta。"""
    meta = {"name": name, "reason": reason, "restart": restart,
            "stopped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    p = Path(sentinel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if notify:  # 终函回调:notify(meta) -> None;失败不阻断停机
        try:
            notify(meta)
        except Exception:
            pass
    return meta


def check_sentinel(sentinel: str) -> tuple[bool, dict | None]:
    """判活方:返回 (stopped, meta)。sentinel 在=停,meta 含重启路径。"""
    p = Path(sentinel)
    if not p.exists():
        return False, None
    try:
        return True, json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return True, {"name": p.stem, "restart": None,
                      "note": "sentinel 存在但不可解析(手写?)"}


def clear_sentinel(sentinel: str) -> None:
    Path(sentinel).unlink(missing_ok=True)
