# -*- coding: utf-8 -*-
"""L2-D 形态自检门(org 通用·2026-10-02):agent 出站前的最后一道自检。
语义源=评委团四门规则(soul_jury_worker·73% 拒率实证):
  独白泄漏/半成品/错通道/旧信息——出站前跑一次,RED 则拒发。
用法:
    from org_lib.output_gate import gate_check
    v = gate_check({"title": "...", "body": "...", "kind": "proposal"})
    if v["status"] == "RED": # 拒发/改写
"""
from __future__ import annotations

import re

# 独白泄漏特征(Selector-derived 系)
_MONOLOGUE = re.compile(
    r"intent_router\||Selector-derived|^我的承诺|^我先说我的判断|"
    r"^计划[::]|^我要|^我注意到|^我开始琢磨|不再\s*planning")
# 半成品标记
_INCOMPLETE = re.compile(r"待确认|TBD|TODO|FIXME|待定|稍后补|\?\?\?")
# 错通道(审计/报告类应走 writeback 不走 proposal)
_WRONG_CHANNEL = re.compile(r"Audit.*报告|审计.*报告|归档$")
# 无工件空话(没有代码/SQL/URL 坐标)
_NO_EVIDENCE = re.compile(
    r"^(?!.*(commit|http|sql|SELECT|INSERT|```).*$)", re.S)


def gate_check(item: dict) -> dict:
    """出站自检。item 至少含 title/body,可选 kind。
    返回 {status: GREEN|RED, reasons: [...]}。"""
    title = str(item.get("title", ""))
    body = str(item.get("body", ""))
    kind = str(item.get("kind", ""))
    blob = title + "\n" + body
    reasons = []

    if _MONOLOGUE.search(blob):
        reasons.append("G-form:独白泄漏(内省文本入出站通道)")
    if _INCOMPLETE.search(blob) and kind == "proposal":
        reasons.append("G-form:半成品(含待确认/TBD 标记)")
    if _WRONG_CHANNEL.search(blob) and kind == "proposal":
        reasons.append("G-form:错通道(审计报告应走 writeback)")
    if kind == "proposal" and len(body) > 100 and not _NO_EVIDENCE.match(body):
        pass  # 有工件,OK
    elif kind == "proposal" and len(body) > 200:
        reasons.append("G-form:无工件(长文本但无代码/SQL/URL 坐标)")

    return {"status": "RED" if reasons else "GREEN", "reasons": reasons,
            "gate": "L2-D output_gate"}
