import json
import pathlib
import sys


def validate_trajectory(data):
    for field in ("qid", "verdict", "label_origin", "trajectory"):
        if field not in data:
            raise ValueError(f"missing {field}")
    if data["label_origin"] == "LLM":
        raise ValueError("LLM self-report not allowed")


def main():
    ok = 0
    bad = 0
    for path in pathlib.Path("trajectories").glob("*.json"):
        try:
            validate_trajectory(json.loads(path.read_text()))
            ok += 1
            print(f"  OK {path.name}")
        except Exception as error:
            print(f"  BAD {path.name}: {error}")
            bad += 1
    print(f"valid={ok} bad={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
