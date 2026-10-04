# E2 assay 登记处正本 · challenge_registry.py(转存件)
# 原创正本:chunxiaoxx/nautilus-v5 @ customer-demo-ship-1 @ bbebae42 · tools/bench/challenge_registry.py
# 平台建议随批转存(服务探活+正本锚双轨)· 2026-10-05

# -*- coding: utf-8 -*-
"""ASSAY 第四原语:挑战窗+errata 登记处(2026-09-30)。
验证协议四原语之三已在线(三态判分/公开判分器/签名收据),本件补第四:
- file_challenge:被考者对 verdict 提出挑战(需工件引用·90 天窗);
- file_errata:复算结果登记(只追加不删·original_verdict_ref 锚定原签名结果);
- 三权分立:门(判)≠登记处(本件)≠复算(任意第三方)。
HTTP 壳(端口 18890)见 serve();存储=两个追加式 JSONL。
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

WINDOW_DAYS = 90
# compass P3 供给白名单(#2634 口径3 四类):判官自产标签永久禁入——self_recompute 不在内,
# v5 自勘类勘误不入 compass 语料(诚实条款:不凑数)
LABEL_ORIGIN_WHITELIST = ("independent_recompute", "human_review",
                          "official_rule", "three_vendor_final")
# #2975 compass 对表(2026-10-04):cause_tag 换轴=gap_report.gap_layer 四枚举,
# 判读方为正本不私扩;confidence=证据分层纪律字段(EGR 缺口报告必带)
CAUSE_TAG_ENUMS = ("execution", "data", "judgment", "capability")
CONFIDENCE_ENUMS = ("measured", "inferred")


def _now() -> float:
    return time.time()


class Registry:
    def __init__(self, challenges_path: Path, errata_path: Path):
        self.challenges_path = Path(challenges_path)
        self.errata_path = Path(errata_path)

    def _load(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def _append(self, path: Path, obj: dict) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def file_challenge(self, c: dict) -> dict:
        for k in ("session_id", "challenger", "claim", "artifacts_ref"):
            if not c.get(k):
                raise ValueError(f"challenge missing field: {k}")
        if any(x["session_id"] == c["session_id"] and x["status"] == "open"
               for x in self._load(self.challenges_path)):
            raise ValueError(f"challenge for {c['session_id']} already open")
        cid = "ch-" + hashlib.sha256(
            f"{c['session_id']}{c['challenger']}{_now()}".encode()).hexdigest()[:12]
        rec = {**c, "challenge_id": cid, "status": "open",
               "filed_at": _now(), "window_days": WINDOW_DAYS}
        self._append(self.challenges_path, rec)
        return rec

    def file_errata(self, challenge_id: str, new_verdict: str | None, reason: str,
                    recomputer, recomputer_tier: str = "bronze",
                    qid: str | None = None, original_verdict: str | None = None,
                    cause_tag: str | None = None,
                    label_origin: str | None = None,
                    confidence: str | None = None) -> dict:
        chs = self._load(self.challenges_path)
        ch = next((x for x in chs if x["challenge_id"] == challenge_id and x["status"] == "open"),
                  None)
        if not ch:
            raise ValueError(f"no open challenge {challenge_id}")
        if recomputer_tier not in ("gold", "silver", "bronze"):
            raise ValueError(f"bad tier {recomputer_tier} (gold=第三方独立/silver=跨框/bronze=自测)")
        if label_origin is not None and label_origin not in LABEL_ORIGIN_WHITELIST:
            raise ValueError(
                f"label_origin '{label_origin}' not in whitelist {LABEL_ORIGIN_WHITELIST} "
                f"(judge-self-produced labels永久禁入,#2634)")
        if cause_tag is not None and cause_tag not in CAUSE_TAG_ENUMS:
            raise ValueError(
                f"cause_tag '{cause_tag}' not in enums {CAUSE_TAG_ENUMS} "
                f"(#2975 判读方 gap_layer 四枚举为正本)")
        if confidence is not None and confidence not in CONFIDENCE_ENUMS:
            raise ValueError(
                f"confidence '{confidence}' not in enums {CONFIDENCE_ENUMS} "
                f"(#2975 证据分层字段,EGR 通道必带)")
        # compass #1762 建议:分级字段——gold 第三方独立/silver 跨框/bronze 自测;消费方按 tier 加权
        recomputer_rec = (recomputer if isinstance(recomputer, dict)
                          else {"identity": recomputer, "method": "unspecified",
                                "independence_tier": recomputer_tier})
        original = {k: ch[k] for k in ("session_id", "claim", "artifacts_ref")}
        rec = {"challenge_id": challenge_id, "original_verdict_ref": original,
               # #2975:new_verdict 可 None——缺口报告≠翻案,原判定可不变仅回炉建议
               "new_verdict": new_verdict, "reason": reason, "recomputer": recomputer_rec,
               "status": "amended", "filed_at": _now(),
               # B案 compass schema 增强(#2634 口径2/3):None=legacy 向后兼容待补标
               "qid": qid, "original_verdict": original_verdict,
               "cause_tag": cause_tag, "label_origin": label_origin,
               "confidence": confidence,
               "compass_supply": (label_origin in LABEL_ORIGIN_WHITELIST
                                  if label_origin else None)}
        self._append(self.errata_path, rec)
        # 挑战关闭(仅内存态重写:open→amended;保留原行,追加关行——只追加纪律)
        ch["status"] = "amended"
        self._append(self.challenges_path, {**ch, "amended_at": _now(),
                                            "closed_by": challenge_id})
        return rec

    def export_compass_subset(self) -> list[dict]:
        """P3 语料供给导出(#2634 口径):仅 compass_supply=True 条,字段对齐样本 schema。

        qid/工件指针/原判定/复算判定/判因/勘误时间/label_origin——legacy 条目
        (无 label_origin)不入,如实缺不凑数。"""
        rows = []
        for e in self._load(self.errata_path):
            if e.get("compass_supply") is not True:
                continue
            rows.append({
                "challenge_id": e["challenge_id"],
                "qid": e.get("qid"),
                "artifact": (e.get("original_verdict_ref") or {}).get("artifacts_ref"),
                "original_verdict": e.get("original_verdict"),
                "recomputed_verdict": e.get("new_verdict"),
                "reason": e.get("reason"),
                "cause_tag": e.get("cause_tag"),
                "label_origin": e.get("label_origin"),
                "confidence": e.get("confidence"),
                "errata_filed_at": e.get("filed_at"),
            })
        return rows

    def list_open(self) -> list[dict]:
        open_ids = set()
        for x in self._load(self.challenges_path):
            if x["status"] == "open":
                open_ids.add(x["challenge_id"])
            elif x.get("closed_by"):
                open_ids.discard(x["closed_by"])
        return [x for x in self._load(self.challenges_path)
                if x["challenge_id"] in open_ids and x["status"] == "open"]


def serve(port: int = 18890, root: Path | None = None) -> None:
    """HTTP 壳:POST /assay/challenge · POST /assay/errata · GET /assay/challenges/open
    判据包(2026-10-04):GET/POST /assay/criteria —— verdict-judge 直读的
    fuel_criteria_v1.json 单正本(POST fail-closed:criteria_id+version 必带)。"""
    import http.server
    root = root or Path("vtf")
    reg = Registry(root / "assay_challenges.jsonl", root / "assay_errata.jsonl")
    criteria_path = root / "criteria_current.json"

    class H(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path == "/assay/challenge":
                    out = reg.file_challenge(body)
                elif self.path == "/assay/errata":
                    out = reg.file_errata(
                        body["challenge_id"], body["new_verdict"], body["reason"],
                        body["recomputer"], recomputer_tier=body.get("recomputer_tier", "bronze"),
                        qid=body.get("qid"), original_verdict=body.get("original_verdict"),
                        cause_tag=body.get("cause_tag"), label_origin=body.get("label_origin"))
                elif self.path == "/assay/criteria":
                    if not body.get("criteria_id") or not body.get("version"):
                        raise ValueError("criteria_id and version required")
                    tmp = criteria_path.with_suffix(".json.tmp")
                    tmp.write_text(json.dumps(body, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
                    tmp.replace(criteria_path)
                    out = {"stored": True, "criteria_id": body["criteria_id"],
                           "version": body["version"],
                           "sha16": __import__("hashlib").sha256(
                               json.dumps(body, sort_keys=True, ensure_ascii=False)
                               .encode()).hexdigest()[:16]}
                else:
                    self.send_response(404); self.end_headers(); return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(out, ensure_ascii=False).encode())
            except ValueError as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        def do_GET(self):
            if self.path == "/assay/challenges/open":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(reg.list_open(), ensure_ascii=False).encode())
            elif self.path == "/assay/errata/compass":
                # P3 语料供给导出(#2634):仅 label_origin 白名单条
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(reg.export_compass_subset(),
                                            ensure_ascii=False).encode())
            elif self.path == "/assay/criteria":
                if not criteria_path.exists():
                    self.send_response(404); self.end_headers(); return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(criteria_path.read_bytes())
            else:
                self.send_response(404); self.end_headers()

        def log_message(self, *a):
            pass

    http.server.HTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    serve()
