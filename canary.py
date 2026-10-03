# -*- coding: utf-8 -*-
"""Deterministic sampling and baseline drift checks for canary evaluations."""
import hashlib
import json


_DRIFT_LIMITS = {
    "legal": 0.10,
    "name": 0.10,
    "args_raw": 0.08,
    "args_norm": 0.10,
}


def build_canary_set(records, seed=20261001, n=40):
    """Select up to ``n`` records deterministically for a canary evaluation."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")

    pool = list(records)
    seed_prefix = str(seed).encode("utf-8")

    def content_key(record):
        content = json.dumps(
            record, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(seed_prefix + b":" + content).digest()

    return sorted(pool, key=content_key)[:n]


def drift_verdict(current, baseline, n=40):
    """Return RED when any measured canary score regresses beyond its limit."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")

    reasons = []
    for metric, limit in _DRIFT_LIMITS.items():
        drop = baseline[metric] - current[metric]
        if drop > limit:
            reasons.append(f"{metric} dropped by {drop:.3f} (limit {limit:.3f})")

    return {"status": "RED" if reasons else "GREEN", "reasons": reasons}
