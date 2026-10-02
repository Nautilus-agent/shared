# -*- coding: utf-8 -*-
"""canary 常驻基准(TDD·2026-10-01·融合方案焊接点②③):
固定 40 题快照(冻结可比)+双轨判分(raw+norm)+漂移判定(对基线快照,过阈值=RED)。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "uni_agent_bridge"))

from canary import build_canary_set, drift_verdict  # noqa: E402


def _mk(i, text=None):
    return {"prompt": [{"role": "user", "content": text or f"issue {i}"}],
            "completion": '{"name": "str_replace_editor", "arguments": {"command": "view", "path": "/repo"}}'}


class TestCanarySet:
    def test_fixed_seed_same_sample(self):
        """同 seed 两次抽样完全一致(漂移可比的前提)。"""
        a = build_canary_set([_mk(i) for i in range(200)], seed=20261001, n=40)
        b = build_canary_set([_mk(i) for i in range(200)], seed=20261001, n=40)
        assert [s["prompt"][0]["content"] for s in a] == [s["prompt"][0]["content"] for s in b]

    def test_size_and_uniqueness(self):
        out = build_canary_set([_mk(i) for i in range(753)], seed=20261001, n=40)
        assert len(out) == 40
        texts = [s["prompt"][0]["content"] for s in out]
        assert len(set(texts)) == 40  # 不重复

    def test_freeze_by_content_hash(self):
        """冻结=内容寻址:题卷指纹稳定。"""
        out = build_canary_set([_mk(i) for i in range(100)], seed=7, n=10)
        out2 = build_canary_set([_mk(i) for i in range(100)], seed=7, n=10)
        assert str(out) == str(out2)


class TestDriftVerdict:
    def test_green_within_threshold(self):
        base = {"legal": 0.99, "name": 0.95, "args_raw": 0.14, "args_norm": 0.30}
        now = {"legal": 0.97, "name": 0.92, "args_raw": 0.10, "args_norm": 0.26}
        v = drift_verdict(now, base, n=40)
        assert v["status"] == "GREEN", v

    def test_red_on_args_crash(self):
        base = {"legal": 0.99, "name": 0.95, "args_raw": 0.14, "args_norm": 0.30}
        now = {"legal": 0.98, "name": 0.90, "args_raw": 0.00, "args_norm": 0.05}
        v = drift_verdict(now, base, n=40)
        assert v["status"] == "RED" and any("args" in r for r in v["reasons"])

    def test_red_on_legal_crash(self):
        base = {"legal": 0.99, "name": 0.95, "args_raw": 0.14, "args_norm": 0.30}
        now = {"legal": 0.75, "name": 0.70, "args_raw": 0.10, "args_norm": 0.20}
        v = drift_verdict(now, base, n=40)
        assert v["status"] == "RED"  # legal 崩=解析能力坏

    def test_improvement_noted_not_red(self):
        base = {"legal": 0.99, "name": 0.95, "args_raw": 0.14, "args_norm": 0.30}
        now = {"legal": 0.99, "name": 0.96, "args_raw": 0.30, "args_norm": 0.50}
        v = drift_verdict(now, base, n=40)
        assert v["status"] == "GREEN"
