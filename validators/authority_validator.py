#!/usr/bin/env python3
"""ARCF Authority Validator — Refactored from Chamber2.py
Checks if evidence status authorizes proposed decision tier."""

from typing import Dict

class AuthorityValidator:
    MATRIX = {
        "metaphorical": {"inform": True, "pilot": False, "automate": False, "max_tier": "T0"},
        "interpretive": {"inform": True, "pilot": False, "automate": False, "max_tier": "T1"},
        "hypothesis": {"inform": True, "pilot": True, "automate": False, "max_tier": "T2"},
        "tested_mechanism": {"inform": True, "pilot": True, "automate": "bounded", "max_tier": "T3"},
        "operationally_validated": {"inform": True, "pilot": True, "automate": "bounded", "max_tier": "T4"},
    }
    TIER_MIN = {
        "T0": (0, 0, 0), "T1": (1, 1, 0), "T2": (2, 2, 1),
        "T3": (3, 3, 2), "T4": (4, 5, 3)
    }

    def check(self, semantic: int, implementation: int, operational: int, tier: str) -> Dict:
        tier = tier.upper()
        mins = self.TIER_MIN.get(tier, (5, 5, 5))
        errors = []
        if semantic < mins[0]: errors.append(f"Semantic {semantic} < {mins[0]} for {tier}")
        if implementation < mins[1]: errors.append(f"Implementation {implementation} < {mins[1]} for {tier}")
        if operational < mins[2]: errors.append(f"Operational {operational} < {mins[2]} for {tier}")
        return {"passed": len(errors) == 0, "validator": "authority", "errors": errors, "tier": tier}

if __name__ == "__main__":
    v = AuthorityValidator()
    print(v.check(3, 4, 2, "T3"))
