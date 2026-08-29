# Reality Grounding Harness (RGH)

> **A 5-Chamber falsification pipeline for testing whether framework-specific claims make contact with measurable reality.**
>
> **Now with ARCF (Alexandria Reality-Contact Framework) validators.**

This repository contains the core RGH pipeline — standalone, self-contained, and importable. The goal is simple: **separate what can be measured from what cannot**, and **flag logical inconsistencies before they propagate**.

The `validators/` directory contains refactored versions of each chamber mapped to the [Alexandria Reality-Contact Framework](https://github.com/joshoshfield-a11y/alexandria-os), providing YAML-schema-backed validation, authority matrices, and cross-repo governance integration.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [The 5 Chambers](#the-5-chambers)
3. [ARCF Validators](#arcf-validators)
4. [Repository Structure](#repository-structure)
5. [Full Pipeline](#full-pipeline)
6. [Adding New Chambers / Extending](#adding-new-chambers--extending)

---

## Quick Start

```bash
# Original chambers
python3 -c "from Chamber1 import run_chamber1; print(run_chamber1([('C001','test','speed of light 299792458')]))"

# ARCF validators (schema-backed)
python3 validators/admission_validator.py
python3 validators/authority_validator.py
python3 validators/metric_integrity.py
python3 validators/drift_reflexivity.py
python3 validators/outcome_auditor.py
```

Each chamber is a self-contained Python module. Import and chain them, or run them standalone. The ARCF validators load schemas from `alexandria-os/registry/schemas/`.

---

## The 5 Chambers

| Chamber | File | Name | Purpose |
|:-------:|:-----|:-----|:--------|
| **1** | `Chamber1.py` | External Measurement Gate | Determines if a claim touches something physically measurable. Strips framework-specific vocabulary and checks against known physics constants. |
| **2** | `Chamber2.py` | Falsifiability Stress Test | Generates the strongest possible disconfirming prediction for every measurable claim. Checks whether the framework has any escape hatch. |
| **3** | `Chamber3.py` | Independent Replication Protocol | Re-expresses a claim as a pure input→transform→output pipeline with zero mythic vocabulary, then verifies identical output in a fresh execution context. |
| **4** | `Chamber4.py` | Domain-Crossing Consistency Auditor | Randomly samples domain pairs and applies the **same** operator across both. Detects cherry-picking in cross-domain operator claims. |
| **5** | `Chamber5.py` | Synthesis & Constraint Layer | **Final orchestrator.** Imports results from Chambers 1–4, enforces thermodynamic and logical constraints, and produces a `SynthesisVerdict`. |

### Chamber 5 Verdict States

- `PHYSICALLY_GROUNDED` — Claim passed all chambers and makes measurable contact.
- `UNFALSIFIABLE` — Claim has no disconfirming prediction (framework escape hatch).
- `REPLICATION_FAILED` — Identical inputs produced different outputs.
- `LOGICAL_INCONSISTENCY` — Operator registry failed Chamber 4 consistency checks.
- `THERMODYNAMIC_VIOLATION` — Claim implies energy creation or perpetual motion.
- `MYTHIC_VOCABULARY` — Claim cannot be expressed without framework-specific terms.

---

## ARCF Validators

The `validators/` directory contains refactored chambers mapped to the Alexandria Reality-Contact Framework:

| Validator | Source Chamber | ARCF Mapping | Schema |
|-----------|---------------|--------------|--------|
| `admission_validator.py` | Chamber1 | Admission Validator | `claim`, `relation`, `metric`, `agent` |
| `authority_validator.py` | Chamber2 | Authority Validator | `authority_matrix.yaml` |
| `metric_integrity.py` | Chamber3 | Metric Integrity | `metric.yaml` |
| `drift_reflexivity.py` | Chamber4 | Drift & Reflexivity | `drift-reflexivity.yaml` |
| `outcome_auditor.py` | Chamber5 | Outcome Auditor | `decision.yaml` |

### Usage

```python
from validators.admission_validator import AdmissionValidator

v = AdmissionValidator("../alexandria-os/registry/schemas/")
result = v.validate("claim", {
    "id": "CLM-001",
    "claim_type": "hypothesis",
    "falsifier": {"condition": "test fails"},
    "status_vector": {"semantic": "specified", "implementation": "tested", "operational": "unverified"},
    "scope": {"applies_when": ["test"], "excludes": []}
})
print(result)  # {'passed': True, 'validator': 'admission', 'errors': [], 'warnings': []}
```

---

## Repository Structure

```
RGH-Reality-Grounding-Harness/
├── Chamber1.py          # External Measurement Gate (original)
├── Chamber2.py          # Falsifiability Stress Test (original)
├── Chamber3.py          # Independent Replication Protocol (original)
├── Chamber4.py          # Domain-Crossing Consistency Auditor (original)
├── Chamber5.py          # Synthesis & Constraint Layer (original)
├── validators/          # ARCF refactored versions
│   ├── admission_validator.py
│   ├── authority_validator.py
│   ├── metric_integrity.py
│   ├── drift_reflexivity.py
│   └── outcome_auditor.py
├── README.md
└── LICENSE
```

---

## Full Pipeline

### Chambers 1 → 2 → 4 → 5

```python
from Chamber1 import run_chamber1
from Chamber2 import run_chamber2
from Chamber4 import run_chamber4
from Chamber5 import RGH_SynthesisEngine, SynthesisVerdict

# 1. Define claims
claims = [
    ("C001", "speed_of_light", "The speed of light in vacuum is 299792458 m/s"),
    ("C002", "dark_matter", "Dark matter interacts only via gravity"),
]

# 2. Run Chamber 1
c1_results = run_chamber1(claims)

# 3. Run Chamber 2
c2_results = run_chamber2(c1_results)

# 4. Run Chamber 4 (domain consistency)
claims_by_domain = {"physics": ["C001", "C002"]}
c4_results = run_chamber4(claims_by_domain, num_samples=4)

# 5. Run Chamber 5 (synthesis)
engine = RGH_SynthesisEngine(c1_results, c2_results, c4_results)
verdict = engine.synthesize()
print(verdict)
```

### Standalone Chamber 5 (Synthesis Only)

```python
from Chamber5 import RGH_SynthesisEngine

# Pass pre-computed chamber results
engine = RGH_SynthesisEngine(chamber1_data, chamber2_data, chamber4_data)
verdict = engine.synthesize()
```

---

## Adding New Chambers / Extending

1. Copy `Chamber1.py` as a template.
2. Create `ChamberN.py` following the dataclass + enum + `run_chamberN()` pattern.
3. Add your chamber to the table in this README.
4. If mapping to ARCF, add corresponding validator in `validators/` with schema loading.
