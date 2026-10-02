# -*- coding: utf-8 -*-
"""L2-D 形态自检门 TDD(2026-10-02):独白泄漏/半成品/错通道/无工件四检。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "org_lib"))

from output_gate import gate_check  # noqa: E402


class TestMonologueLeak:
    def test_selector_derived_rejected(self):
        v = gate_check({"title": "Selector-derived proposal", "body": "intent_router|evolve:计划...", "kind": "proposal"})
        assert v["status"] == "RED"

    def test_inner_monologue_rejected(self):
        v = gate_check({"title": "x", "body": "我的承诺是:不再 planning,直接投", "kind": "proposal"})
        assert v["status"] == "RED"

    def test_normal_proposal_passes(self):
        v = gate_check({"title": "fix: improve cache", "body": "commit abc123 ```python\nx=1\n```", "kind": "proposal"})
        assert v["status"] == "GREEN"


class TestIncomplete:
    def test_tbd_rejected_for_proposal(self):
        v = gate_check({"title": "wire X", "body": "路径待确认,先这样", "kind": "proposal"})
        assert v["status"] == "RED"

    def test_tbd_ok_for_non_proposal(self):
        v = gate_check({"title": "wire X", "body": "路径待确认,先这样", "kind": "mail"})
        assert v["status"] == "GREEN"


class TestWrongChannel:
    def test_audit_report_rejected_for_proposal(self):
        v = gate_check({"title": "Audit 异常扫描报告", "body": "24h error 审计报告归档", "kind": "proposal"})
        assert v["status"] == "RED"


class TestGreen:
    def test_clean_proposal(self):
        v = gate_check({"title": "feat: add endpoint", "body": "commit 123\n```sql\nSELECT 1;\n```", "kind": "proposal"})
        assert v["status"] == "GREEN"
        assert v["reasons"] == []
