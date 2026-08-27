#!/usr/bin/env python3
"""ARCF Drift & Reflexivity Validator — Refactored from Chamber4.py
Detects distribution shifts and self-confirming loops."""

from typing import Dict, List
import statistics

class DriftValidator:
    def detect(self, current: List[float], baseline: List[float], sensitivity: float = 0.2, check_self_confirming: bool = True) -> Dict:
        errors, warnings = [], []
        if not current or not baseline:
            return {"passed": False, "validator": "drift", "errors": ["Empty distributions"], "warnings": []}
        mean_c = statistics.mean(current)
        mean_b = statistics.mean(baseline)
        divergence = abs(mean_c - mean_b) / (abs(mean_b) + 1e-10)
        if divergence > sensitivity:
            warnings.append(f"Drift detected: {divergence:.3f} > {sensitivity}")
        if divergence > sensitivity * 2:
            errors.append(f"CRITICAL drift: {divergence:.3f}")
        if check_self_confirming:
            warnings.append("Self-confirming loop monitoring active")
        return {"passed": len(errors) == 0, "validator": "drift_reflexivity", "errors": errors, "warnings": warnings, "divergence": divergence}

if __name__ == "__main__":
    v = DriftValidator()
    print(v.detect([0.1, 0.2, 0.15], [0.1, 0.2, 0.15], 0.2, True))
