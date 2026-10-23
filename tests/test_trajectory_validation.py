import json
from pathlib import Path

import pytest

from validate_trajectories import validate_trajectory


FIXTURES = Path(__file__).parent / "fixtures"
TRAJECTORIES = Path(__file__).parents[1] / "trajectories"


def test_accepts_human_verified_trajectory():
    data = json.loads((TRAJECTORIES / "kairos_probe_valid_20261023.json").read_text())
    validate_trajectory(data)


def test_rejects_llm_origin_trajectory():
    data = json.loads((FIXTURES / "kairos_probe_llm_origin_20261023.json").read_text())
    with pytest.raises(ValueError, match="LLM self-report not allowed"):
        validate_trajectory(data)


def test_rejects_missing_required_field():
    with pytest.raises(ValueError, match="missing trajectory"):
        validate_trajectory(
            {"qid": "q1", "verdict": "pass", "label_origin": "human_verified"}
        )
