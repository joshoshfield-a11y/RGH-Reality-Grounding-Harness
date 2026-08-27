#!/usr/bin/env python3
"""ARCF Admission Validator — Refactored from Chamber1.py
Validates records against alexandria-os registry schemas."""

import yaml
from pathlib import Path
from typing import Dict, List, Any

class AdmissionValidator:
    def __init__(self, schema_dir: str = "../alexandria-os/registry/schemas/"):
        self.schemas = {}
        for f in Path(schema_dir).glob("*.yaml"):
            with open(f) as fh:
                self.schemas[f.stem] = yaml.safe_load(fh)

    def validate(self, record_type: str, record: Dict[str, Any]) -> Dict[str, Any]:
        schema = self.schemas.get(record_type)
        if not schema:
            return {"passed": False, "error": f"No schema: {record_type}"}
        errors, warnings = [], []
        required = schema.get("required", [])
        for field in required:
            if field not in record:
                errors.append(f"Missing: {field}")
        if record_type == "claim":
            if record.get("claim_type") == "metaphorical" and record.get("decision_rights", {}).get("may_automate"):
                errors.append("REJECT: Metaphorical claims cannot automate")
            if "falsifier" not in record:
                errors.append("REJECT: Missing falsifier")
            if "status_vector" not in record:
                errors.append("REJECT: Missing status_vector")
        elif record_type == "relation":
            if "relation_type" not in record:
                errors.append("REJECT: Missing relation_type")
            if "preservation_contract" not in record:
                errors.append("REJECT: Missing preservation_contract")
            if len(record.get("oracles", [])) < 1:
                errors.append("REJECT: Missing oracles")
        elif record_type == "metric":
            if len(record.get("counter_metrics", [])) < 1:
                errors.append("REJECT: Missing counter_metrics")
            if len(record.get("gaming_paths", [])) < 1:
                errors.append("REJECT: Missing gaming_paths")
        return {"passed": len(errors) == 0, "validator": "admission", "errors": errors, "warnings": warnings}

if __name__ == "__main__":
    v = AdmissionValidator()
    test = {"id": "CLM-001", "kind": "claim", "title": "T", "statement": "S",
            "claim_type": "hypothesis", "scope": {}, "status_vector": {},
            "evidence": {}, "falsifier": {}, "decision_rights": {}, "review": {}}
    print(v.validate("claim", test))
