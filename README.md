# Reality Grounding Harness (RGH)

> **A 5-Chamber falsification pipeline for testing whether framework-specific claims make contact with measurable reality.**

This repository is designed as a **living, operational system**. Every chamber is a standalone module that can be run independently or chained together. The goal is simple: **separate what can be measured from what cannot**, and **flag logical inconsistencies before they propagate**.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [The 5 Chambers](#the-5-chambers)
3. [Repository Structure](#repository-structure)
4. [Skills & Tools Section](#skills--tools-section)
5. [Usage Examples](#usage-examples)
6. [Adding New Chambers / Extending](#adding-new-chambers--extending)
7. [License](#license)

---

## Quick Start

```bash
git clone https://github.com/joshoshfield-a11y/RGH-Reality-Grounding-Harness.git
cd RGH-Reality-Grounding-Harness
python3 -c "from Chamber1 import run_chamber1; print(run_chamber1([('C001','test','speed of light 299792458')]))"
```

Each chamber is a self-contained Python module. Import and chain them, or run them standalone.

---

## The 5 Chambers

| Chamber | File | Name | Purpose |
|---------|------|------|---------|
| **1** | `Chamber1.py` | External Measurement Gate | Determines if a claim touches something physically measurable. Strips framework-specific vocabulary and checks against known physics constants. |
| **2** | `Chamber2.py` | Falsifiability Stress Test | Generates the strongest possible disconfirming prediction for every measurable claim. Checks whether the framework has any escape hatch. |
| **3** | `Chamber3.py` | Independent Replication Protocol | Re-expresses a claim as a pure input→transform→output pipeline with zero mythic vocabulary, then verifies identical output in a fresh execution context. |
| **4** | `Chamber4.py` | Domain-Crossing Consistency Auditor | Randomly samples domain pairs and applies the **same** operator across both. Detects cherry-picking in cross-domain operator claims. |
| **5** | `Chamber5.py` | Synthesis & Constraint Layer | **Final orchestrator.** Imports results from Chambers 1–4, enforces thermodynamic and logical constraints, and produces a `SynthesisVerdict`. |

### Chamber 5 Verdict States

- `SYSTEM_STABLE` — All claims passed or are explicitly marked as hypotheses.
- `THERMODYNAMIC_VIOLATION` — Energy extraction claims failed thermodynamic guardrails (e.g., Casimir/DCE limits).
- `LOGICAL_INCONSISTENCY` — Operator registry failed Chamber 4 consistency checks.
- `FRAMEWORK_HALLUCINATION` — Attempted to bridge gaps with unconstrained variables.

---

## Repository Structure

```
RGH-Reality-Grounding-Harness/
├── Chamber1.py          # External Measurement Gate
├── Chamber2.py          # Falsifiability Stress Test
├── Chamber3.py          # Independent Replication Protocol
├── Chamber4.py          # Domain-Crossing Consistency Auditor
├── Chamber5.py          # Synthesis & Constraint Layer
├── README.md            # You are here
├── LICENSE              # Custom license (see below)
└── skills/              # Cross-session reusable tools & skills
    └── (add your own)
```

### What Goes Where

- **Chamber files (`Chamber1.py`–`Chamber5.py`)** — Core pipeline. Treat these as immutable reference implementations. If you extend a chamber, version it (e.g., `Chamber4_v2.py`).
- **`skills/`** — This is the ** Skills & Tools Section**. Drop reusable utilities here: custom operators, new framework vocab mappings, domain-specific claim extractors, visualization helpers, or integration adapters. These are meant to be **easily accessible across sessions** — import them into any chamber or external script.
- **`LICENSE`** — Custom license. Free for public/non-commercial use. Commercial use requires a paid license from the author.

---

## Skills & Tools Section

The `skills/` directory is where you store **reusable, cross-session components** that extend the RGH pipeline without modifying the core chambers.

### Examples of what to put here:

| Skill | Description |
|-------|-------------|
| `skills/framework_vocab.py` | Extended `FRAMEWORK_VOCAB` dictionaries for new domains (e.g., biophysics, cryptography). |
| `skills/physics_constants.py` | Additional physics constants beyond the base set (e.g., Schwinger limit, Planck energy). |
| `skills/claim_extractors.py` | NLP or regex-based extractors that pull claims from PDFs, markdown, or raw text corpora. |
| `skills/visualizers.py` | Matplotlib / Plotly dashboards for rendering chamber output as audit reports. |
| `skills/domain_operators.py` | New shared operators for Chamber 4 (e.g., `log_reduction`, `phi_scaling`). |

### How to use a skill:

```python
from skills.physics_constants import EXTENDED_PHYSICS_CONSTANTS
from Chamber1 import classify_claim

# Now your chamber has access to extended constants
```

**Rule of thumb:** If you find yourself copy-pasting the same helper across multiple sessions, it belongs in `skills/`.

---

## Usage Examples

### Full Pipeline (Chambers 1 → 2 → 4 → 5)

```python
from Chamber1 import run_chamber1
from Chamber2 import run_chamber2
from Chamber4 import run_chamber4
from Chamber5 import RGH_SynthesisEngine, SynthesisVerdict

# 1. Define claims
claims = [
    ("C001", "doc.md", "The system aggregates public radio and radar data."),
    ("C002", "doc.md", "The dodecahedral cavity extracts 10^8 J from quantum vacuum."),
]

# 2. Run Chamber 1
c1_results = run_chamber1(claims)

# 3. Run Chamber 2
c2_results = run_chamber2(c1_results)

# 4. Run Chamber 4 (domain consistency)
claims_by_domain = {
    "physics": ["speed of light 299792458", "gravitational curvature 13.0"],
    "structure": ["dodecahedron face count 12", "layer depth 13"],
}
c4_results = run_chamber4(claims_by_domain, num_samples=4)

# 5. Run Chamber 5 (synthesis)
engine = RGH_SynthesisEngine(c1_results, c2_results, c4_results)
verdict = engine.synthesize()

print(verdict.status)      # e.g., SYSTEM_STABLE or LOGICAL_INCONSISTENCY
print(verdict.summary)
print(verdict.action_items)
```

### Standalone Chamber 5 (Synthesis Only)

```python
from Chamber5 import RGH_SynthesisEngine

# Pass pre-computed chamber results
engine = RGH_SynthesisEngine(chamber1_data, chamber2_data, chamber4_data)
verdict = engine.synthesize()

# Check thermodynamic guardrail on a specific claim
is_valid = engine.check_thermodynamics("C002", energy_output_claim=1e8)
```

---

## Adding New Chambers / Extending

1. **Fork or branch** this repo.
2. Create `ChamberN.py` following the dataclass + enum + `run_chamberN()` pattern.
3. Add your chamber to the table in this README.
4. If you build reusable tools, drop them in `skills/`.
5. **Never delete existing files** — this repo follows an append-only doctrine. Version new iterations rather than overwriting.

---

## License

See [LICENSE](LICENSE).

- **Public / Non-Commercial:** Free to use, modify, distribute.
- **Commercial Use:** Requires a paid license from Taylor Christian Mattheisen.
- **Third-Party Conflict:** If any portion is found to infringe on pre-existing licensed work, that portion reverts to the original rightsholder's terms.

---

*Built by Taylor Christian Mattheisen (Skit / Dogbytes) — 2026*
