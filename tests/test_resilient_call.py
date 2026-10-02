# -*- coding: utf-8 -*-
"""org 出站调用规范件(TDD·L2-A·2026-10-01):熔断模式抽域无关配方。
语义源:nautilus_v5/runtime/llm_client.py 风暴三修(27,388 条错误日志事故)。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "org_lib"))

from resilient_call import CircuitOpenError, FatalError, ResilientCaller  # noqa: E402


def _ok(x=None):
    return lambda: x if x is not None else "ok"


class TestRetryPolicy:
    def test_retryable_up_to_max_then_raise(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            raise ConnectionError("refused")

        c = ResilientCaller(name="t", max_retries=3, base_delay=0)
        try:
            c.call(flaky)
            assert False
        except ConnectionError:
            assert calls["n"] == 3  # 1 次 + 2 重试

    def test_fatal_no_retry(self):
        calls = {"n": 0}

        def bad_key():
            calls["n"] += 1
            raise FatalError("401")

        c = ResilientCaller(name="t", max_retries=3, base_delay=0)
        try:
            c.call(bad_key)
            assert False
        except FatalError:
            assert calls["n"] == 1  # 一次即停

    def test_success_after_retry(self):
        state = {"n": 0}

        def flaky_then_ok():
            state["n"] += 1
            if state["n"] < 2:
                raise ConnectionError("x")
            return "done"

        c = ResilientCaller(name="t", max_retries=3, base_delay=0)
        assert c.call(flaky_then_ok) == "done"


class TestCircuitBreaker:
    def test_opens_after_consecutive_failures_and_fails_fast(self):
        calls = {"n": 0}

        def always_fail():
            calls["n"] += 1
            raise ConnectionError("x")

        c = ResilientCaller(name="t", max_retries=1, base_delay=0,
                            breaker_threshold=2, breaker_cooldown=60)
        for _ in range(2):  # 两轮各 1 次调用=2 次连续失败
            try:
                c.call(always_fail)
            except ConnectionError:
                pass
        assert c.breaker_state() == "open"
        n_before = calls["n"]
        try:
            c.call(always_fail)
            assert False
        except CircuitOpenError:  # 快速失败:零出站
            assert calls["n"] == n_before

    def test_fatal_also_opens_breaker_with_long_cooldown(self):
        def bad():
            raise FatalError("401")

        c = ResilientCaller(name="t", max_retries=1, base_delay=0,
                            breaker_threshold=1, breaker_cooldown=3600)
        try:
            c.call(bad)
        except FatalError:
            pass
        assert c.open_until > time.time() + 3500  # 长冷却

    def test_closes_after_cooldown(self):
        c = ResilientCaller(name="t", max_retries=1, base_delay=0,
                            breaker_threshold=1, breaker_cooldown=0.05)
        try:
            c.call(lambda: (_ for _ in ()).throw(ConnectionError("x")))
        except ConnectionError:
            pass
        time.sleep(0.08)
        assert c.call(_ok("recovered")) == "recovered"


class TestSentinel:
    def test_sentinel_written_while_open_removed_on_close(self, tmp_path):
        sentinel = tmp_path / "t.pause"
        c = ResilientCaller(name="t", max_retries=1, base_delay=0,
                            breaker_threshold=1, breaker_cooldown=3600,
                            sentinel_path=str(sentinel))
        try:
            c.call(lambda: (_ for _ in ()).throw(FatalError("401")))
        except FatalError:
            pass
        assert sentinel.exists()  # 自停协议 C:停必留痕
        c.reset()
        assert not sentinel.exists()
