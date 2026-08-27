#!/usr/bin/env python3
"""ARCF Metric Integrity Validator — Refactored from Chamber3.py
Checks counter-metrics, gaming paths, off-dashboard audit, expiry."""

from typing import Dict, Any

class MetricIntegrityValidator:
    def audit(self, metric: Dict[str, Any], gaming_min: int = 2, counter_min: int = 1) -> Dict:
        errors, warnings = [], []
        gaming = metric.get("gaming_paths", [])
        if len(gaming) < gaming_min:
            warnings.append(f"Gaming paths ({len(gaming)}) below minimum ({gaming_min})")
        if len(gaming) < 1:
            errors.append("REJECT: No gaming model")
        counters = metric.get("counter_metrics", [])
        if len(counters) < counter_min:
            errors.append("REJECT: Insufficient counter-metrics")
        off_dashboard = metric.get("off_dashboard_audit")
        if not off_dashboard or not off_dashboard.get("method"):
            errors.append("REJECT: Missing off-dashboard audit")
        expiry = metric.get("expiry")
        if not expiry or not expiry.get("review_after_days"):
            errors.append("REJECT: Missing expiry rule")
        return {"passed": len(errors) == 0, "validator": "metric_integrity", "errors": errors, "warnings": warnings}

if __name__ == "__main__":
    v = MetricIntegrityValidator()
    test = {"counter_metrics": ["error_rate"], "gaming_paths": ["superficial"],
            "off_dashboard_audit": {"method": "blind", "cadence": "weekly"},
            "expiry": {"review_after_days": 30}}
    print(v.audit(test))
