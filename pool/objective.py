"""DoD-1 - read the declared objective + hour budget from memory/objective.md.

OBJECTIVE (HYBRID) and HOUR_CAP_HOURS (6) are a HITL invariant: Sebas decides, Code records + reads.
The cap is a STOP-BY-HITL-CONVENTION (when the budget is reached, STOP and ask for a new GO); it is NOT
auto-enforced here. This module only PARSES and EXPOSES the governing values so every session sees the
same objective. Pure stdlib.
"""
from __future__ import annotations
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJECTIVE_PATH = os.path.join(ROOT, "memory", "objective.md")
VALID_OBJECTIVES = {"MONEY-EV", "LEARNING", "HYBRID"}


def read_objective(path: str = OBJECTIVE_PATH) -> dict:
    """Parse memory/objective.md -> {objective, hour_cap_hours, decided_utc, path}.

    Raises FileNotFoundError if undeclared, ValueError if the two governing keys are absent/invalid.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"objective not declared: {path} missing (run DoD-1)")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m_obj = re.search(r"^OBJECTIVE:\s*(\S+)", text, re.MULTILINE)
    m_cap = re.search(r"^HOUR_CAP_HOURS:\s*([0-9]+(?:\.[0-9]+)?)", text, re.MULTILINE)
    if not m_obj or not m_cap:
        raise ValueError("objective.md must define OBJECTIVE and HOUR_CAP_HOURS")
    objective = m_obj.group(1)
    if objective not in VALID_OBJECTIVES:
        raise ValueError(f"OBJECTIVE={objective!r} not in {sorted(VALID_OBJECTIVES)}")
    m_utc = re.search(r"^DECIDED_UTC:\s*(\S+)", text, re.MULTILINE)
    return {
        "objective": objective,
        "hour_cap_hours": float(m_cap.group(1)),
        "decided_utc": m_utc.group(1) if m_utc else None,
        "path": path,
    }


def banner() -> str:
    """One-line session banner surfacing the governing objective."""
    try:
        o = read_objective()
        return (f"OBJECTIVE={o['objective']} · HOUR_CAP={o['hour_cap_hours']:g}h "
                f"(STOP by HITL convention) · decided {o['decided_utc']}")
    except (FileNotFoundError, ValueError) as e:
        return f"OBJECTIVE undeclared ({e})"


def _selftest():
    o = read_objective()
    assert o["objective"] in VALID_OBJECTIVES, o
    assert o["hour_cap_hours"] > 0, o
    print("objective self-test: PASS")
    print(f"  parsed: {o['objective']} / {o['hour_cap_hours']:g}h  (decided {o['decided_utc']})")
    print(" ", banner())


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _selftest()
