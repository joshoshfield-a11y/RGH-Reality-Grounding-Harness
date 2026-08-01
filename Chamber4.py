"""
RGH Chamber 4: Domain-Crossing Consistency Auditor
Reality Grounding Harness — Chamber 4 of 4

Purpose: Check whether claims that assert the same underlying grammar/operator
applies across different domains (e.g., GR physics, Newtonian physics, Base-13
structure, Tree of Life) actually hold up under RANDOM sampling of domain pairs,
rather than letting the user hand-pick which pairs to test (cherry-pick risk).

Output states:
- CONSISTENT_ACROSS_SAMPLED_DOMAINS
- INCONSISTENT_CHERRY_PICK_RISK
- INSUFFICIENT_DATA
"""

import re
import random
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class ConsistencyFlag(Enum):
    CONSISTENT = "CONSISTENT_ACROSS_SAMPLED_DOMAINS"
    INCONSISTENT = "INCONSISTENT_CHERRY_PICK_RISK"
    INSUFFICIENT = "INSUFFICIENT_DATA"


@dataclass
class Chamber4Result:
    claim_pair: str
    domain_a: str
    domain_b: str
    operator_applied: str
    result_a: str
    result_b: str
    flag: str
    reason: str


def apply_shared_operator(value: str, operator_name: str = "mod_13_reduction") -> Optional[float]:
    """
    Apply the SAME operator identically regardless of domain. This is the
    critical design constraint: the operator must not be adjusted per-domain,
    or the test becomes exactly the cherry-picking it is meant to detect.

    Extend this function with additional operator_name branches to test
    alternative shared operators (the current build ships with mod-13
    reduction only, per initial test).
    """
    match = re.search(r'\d+(\.\d+)?', value)
    if not match:
        return None
    numeric = float(match.group())

    if operator_name == "mod_13_reduction":
        return numeric % 13
    # Add alternative operators here, e.g.:
    # if operator_name == "log_reduction":
    #     import math
    #     return math.log(numeric + 1)
    raise ValueError(f"Unknown operator_name: {operator_name}")


def run_chamber4(claims_by_domain: dict, num_samples: int = 10,
                  operator_name: str = "mod_13_reduction", seed: int = 42) -> list:
    """
    claims_by_domain: dict mapping domain_name -> list of claim strings
        (each claim string should contain at least one numeric value).
    num_samples: number of random domain-pair trials to run.
    operator_name: which shared operator to test (must not vary per domain).
    seed: fixed seed for reproducibility of the random sampling itself.
    """
    random.seed(seed)
    domains = list(claims_by_domain.keys())
    results = []

    if len(domains) < 2:
        return results

    for _ in range(num_samples):
        dom_a, dom_b = random.sample(domains, 2)
        claim_a = random.choice(claims_by_domain[dom_a])
        claim_b = random.choice(claims_by_domain[dom_b])

        res_a = apply_shared_operator(claim_a, operator_name)
        res_b = apply_shared_operator(claim_b, operator_name)

        if res_a is None or res_b is None:
            flag = ConsistencyFlag.INSUFFICIENT
            reason = "One or both claims lack a numeric value to apply the shared operator to."
        elif abs(res_a - res_b) < 1e-6:
            flag = ConsistencyFlag.CONSISTENT
            reason = "Same operator produced matching result across both randomly sampled domains."
        else:
            flag = ConsistencyFlag.INCONSISTENT
            reason = (f"Operator produced divergent results ({res_a} vs {res_b}); "
                       f"mapping may require special-casing = cherry-pick risk.")

        results.append(Chamber4Result(
            claim_pair=f"{dom_a}<->{dom_b}",
            domain_a=dom_a, domain_b=dom_b,
            operator_applied=operator_name,
            result_a=str(res_a), result_b=str(res_b),
            flag=flag.value, reason=reason
        ))

    return results


if __name__ == "__main__":
    import pandas as pd

    claims_by_domain = {
        "GR_physics": ["speed of light 299792458 m/s", "gravitational curvature radius 13.0"],
        "Newtonian_physics": ["force equals 26.0 units", "orbital period 39 days"],
        "Base13_structure": ["dodecahedron face count 12", "layer depth 13"],
        "Tree_of_Life": ["sephirot count 10", "path count 22"],
    }
    results = run_chamber4(claims_by_domain, num_samples=6)
    df = pd.DataFrame([asdict(r) for r in results])
    print(df.to_string(index=False))