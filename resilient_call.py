# -*- coding: utf-8 -*-
"""org 出站调用规范件(L2-A·2026-10-01):域无关熔断配方。
语义源=nautilus_v5/runtime/llm_client.py 风暴三修(27,388 条上游错误日志事故):
  ①致命错误(401/403 类)一次即停+长冷却+拉黑——重试是纯浪费
  ②可重试错误(ConnectionError/超时)重试≤max,指数退避
  ③连续失败≥threshold → 熔断打开:期间一切调用快速失败**零出站**(风暴引擎教训:带错误也真发)
  ④冷却期满自动半开试探
  ⑤自停协议 C 接口:熔断打开落 sentinel 文件,恢复删除——停必留痕,不是消失
纯标准库,零依赖,org 各框可直接拷贝或 import。用法:
  caller = ResilientCaller(name="my-api", max_retries=3, breaker_threshold=5)
  resp = caller.call(lambda: requests.get(url, timeout=10).json(),
                     is_fatal=lambda e: isinstance(e, MyAuthError))
"""
from __future__ import annotations

import os
import random
import time
from pathlib import Path


class FatalError(RuntimeError):
    """致命错误(401/403/配置错):换配置前重试是纯浪费,立即熔断。"""


class CircuitOpenError(RuntimeError):
    """熔断打开中:本次调用零出站直接拒绝。"""


class ResilientCaller:
    def __init__(self, name: str, max_retries: int = 3, base_delay: float = 0.5,
                 breaker_threshold: int = 5, breaker_cooldown: float = 60.0,
                 fatal_cooldown: float = 3600.0, sentinel_path: str | None = None):
        self.name = name
        self.max_retries = max(1, max_retries)
        self.base_delay = base_delay
        self.breaker_threshold = max(1, breaker_threshold)
        self.breaker_cooldown = breaker_cooldown
        self.fatal_cooldown = fatal_cooldown
        self.sentinel_path = sentinel_path
        self._consecutive_failures = 0
        self._open_until = 0.0

    # ── 状态 ──
    @property
    def open_until(self) -> float:
        return self._open_until

    def breaker_state(self) -> str:
        return "open" if time.time() < self._open_until else "closed"

    def reset(self) -> None:
        self._consecutive_failures = 0
        self._open_until = 0.0
        self._remove_sentinel()

    # ── sentinel(自停协议 C)──
    def _write_sentinel(self):
        if self.sentinel_path:
            try:
                Path(self.sentinel_path).parent.mkdir(parents=True, exist_ok=True)
                Path(self.sentinel_path).write_text(
                    f"breaker={self.name} open_until={self._open_until} "
                    f"ts={time.strftime('%FT%TZ', time.gmtime())}\n", encoding="utf-8")
            except OSError:
                pass

    def _remove_sentinel(self):
        if self.sentinel_path:
            try:
                Path(self.sentinel_path).unlink(missing_ok=True)
            except OSError:
                pass

    # ── 核心 ──
    def _trip(self, cooldown: float):
        self._open_until = time.time() + cooldown
        self._write_sentinel()

    def call(self, fn, is_fatal=None):
        """执行 fn(无参 callable)。is_fatal(e)->bool 标记致命错误类。"""
        if time.time() < self._open_until:
            raise CircuitOpenError(f"[{self.name}] breaker open until {self._open_until:.0f},零出站拒绝")
        last = None
        for attempt in range(self.max_retries):
            try:
                out = fn()
                self._consecutive_failures = 0
                self._remove_sentinel()
                return out
            except Exception as e:  # noqa: BLE001
                last = e
                if is_fatal and is_fatal(e) or isinstance(e, FatalError):
                    self._consecutive_failures += self.breaker_threshold  # 致命直接顶满
                    self._trip(self.fatal_cooldown)
                    raise
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt) * (1 + random.random() * 0.1))
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.breaker_threshold:
            self._trip(self.breaker_cooldown)
        raise last


def env_caller(name: str, **kw) -> ResilientCaller:
    """从环境变量读参数的便捷构造(V5 风格:ORGCALL_MAX_RETRIES 等)。"""
    get = lambda k, d: type(d)(os.environ.get(f"ORGCALL_{k}", d))  # noqa: E731
    return ResilientCaller(name=name,
                           max_retries=get("MAX_RETRIES", kw.get("max_retries", 3)),
                           breaker_threshold=get("BREAKER_THRESHOLD", kw.get("breaker_threshold", 5)),
                           breaker_cooldown=get("BREAKER_COOLDOWN", kw.get("breaker_cooldown", 60.0)))
