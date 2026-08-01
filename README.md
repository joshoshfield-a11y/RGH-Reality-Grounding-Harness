# Reality Grounding Harness (RGH)

A 4-Chamber falsification pipeline for testing whether framework-specific claims make contact with measurable reality.

## Chambers

| Chamber | Name | Purpose |
|---------|------|---------|
| 1 | External Measurement Gate | Determines if a claim touches something physically measurable |
| 2 | Falsifiability Stress Test | Generates strongest disconfirming prediction and checks for escape hatches |
| 3 | Independent Replication Protocol | Re-expresses claim as code pipeline and verifies identical output in fresh context |
| 4 | Domain-Crossing Consistency Auditor | Random-samples domain pairs to detect cherry-picking in cross-domain operator claims |

## Usage

```python
from Chamber1 import run_chamber1
from Chamber2 import run_chamber2
from Chamber3 import run_chamber3
from Chamber4 import run_chamber4

# Chamber 1: classify claims
claims = [("C001", "doc.md", "The system aggregates public radio data.")]
c1_results = run_chamber1(claims)

# Chamber 2: falsifiability test
c2_results = run_chamber2(c1_results)

# Chamber 3: replication
c3_results = run_chamber3(c1_results, {"C001": "The system aggregates public radio data."})

# Chamber 4: domain consistency
claims_by_domain = {
    "physics": ["speed 299792458"],
    "structure": ["layer depth 13"]
}
c4_results = run_chamber4(claims_by_domain, num_samples=4)
```

## License

See [LICENSE](LICENSE). Free for public/non-commercial use. Commercial use requires paid license from Taylor Christian Mattheisen.
