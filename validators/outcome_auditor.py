#!/usr/bin/env python3
"""ARCF Outcome Auditor — Chamber5
Post-deployment real outcome vs metric comparison."""

from typing import Dict, Any

class OutcomeAuditor:
    def audit(self, decision: Dict[str, Any], real_outcomes: Dict[str, Any]) -> Dict:
        errors, warnings = [], []
        intended = decision.get("intended_outcome")
        actual = real_outcomes.get("measured_outcome")
        if not actual:
            errors.append("REJECT: No real outcome data collected")
        primary_metric = decision.get("primary_metric")
        real_primary = real_outcomes.get(primary_metric)
        if real_primary is None:
            warnings.append(f"Primary metric '{primary_metric}' not measured in reality")
        counter = decision.get("counter_metric")
        real_counter = real_outcomes.get(counter)
        if real_counter is None:
            warnings.append(f"Counter metric '{counter}' not measured")
        delayed = real_outcomes.get("delayed_effects")
        if not delayed:
            warnings.append("No delayed effect check performed")
        return {"passed": len(errors) == 0, "validator": "outcome_auditor", "errors": errors, "warnings": warnings, "intended_vs_actual": (intended, actual)}

if __name__ == "__main__":
    v = OutcomeAuditor()
    decision = {"intended_outcome": "reduce rework", "primary_metric": "rework_rate", "counter_metric": "error_rate"}
    outcomes = {"measured_outcome": "rework reduced 15%", "rework_rate": 0.15, "error_rate": 0.08, "delayed_effects": "none observed"}
    print(v.audit(decision, outcomes))
