"""
RGH Chamber 4: Domain-Crossing Consistency Auditor
Reality Grounding Harness — Chamber 4 of 5 (v0.2)

Purpose: Check whether claims that assert the same underlying operator
applies across different domains actually hold up under RANDOM sampling
of domain pairs, rather than letting the user hand-pick which pairs to
test (cherry-pick risk).

v0.2 changes:
- Named operator REGISTRY. operator_name is now REQUIRED — v0.1 silently
  defaulted to mod-13 reduction, so every "consistency" verdict was
  numerology (residue coincidence). Callers must choose an operator and
  defend the choice.
- mod_13_reduction is kept as LEGACY for backwards compatibility and
  marked as numerological. Prefer a defined operator.
- A CONSISTENT verdict means the same function was applied to both
  domains' quantities — syntactic consistency only. It is NOT evidence
  that the domains share a mechanism. The reason string says so.

Output states:
- CONSISTENT_ACROSS_SAMPLED_DOMAINS
- INCONSISTENT_CHERRY_PICK_RISK
- INSUFFICIENT_DATA
"""

import re
import random
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Callable


class ConsistencyFlag(Enum):
    CONSISTENT = "CONSISTENT_ACROSS_SAMPLED_DOMAINS"
    INCONSISTENT = "INCONSISTENT_CHERRY_PICK_RISK"
    INSUFFICIENT = "INSUFFICIENT_DATA"


@dataclass
class OperatorSpec:
    name: str
    function: Callable[[float], float]
    input_domain: str   # what kind of quantity this operator is defined for
    status: str         # DEFINED or LEGACY


def _metcalfe(n: float) -> float:
    """Metcalfe's law: network value scales as n^2 (Op 55, UT-ITD)."""
    return n ** 2


def _identity(x: float) -> float:
    """Control operator: the null hypothesis that 'the same operator'
    means 'no transformation'. Any CONSISTENT verdict under a real
    operator should also hold trivially here; if it doesn't, the
    extraction (not the operator) is broken."""
    return x


def _mod13(x: float) -> float:
    return x % 13


REGISTRY = {
    "identity": OperatorSpec(
        name="identity",
        function=_identity,
        input_domain="any numeric quantity (control)",
        status="DEFINED",
    ),
    "metcalfe_scaling": OperatorSpec(
        name="metcalfe_scaling",
        function=_metcalfe,
        input_domain="network node counts (n >= 0)",
        status="DEFINED",
    ),
    "mod_13_reduction": OperatorSpec(
        name="mod_13_reduction",
        function=_mod13,
        input_domain="any numeric quantity",
        status="LEGACY — numerological; residue coincidence is not mechanism "
               "agreement. Kept for backwards compatibility only.",
    ),
}


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


def apply_shared_operator(value: str, operator_name: str) -> Optional[float]:
    """
    Apply the SAME operator identically regardless of domain. This is the
    critical design constraint: the operator must not be adjusted per-domain,
    or the test becomes exactly the cherry-picking it is meant to detect.
    """
    if operator_name not in REGISTRY:
        raise ValueError(
            f"Unknown operator '{operator_name}'. Choose from REGISTRY: "
            f"{sorted(REGISTRY)}")
    match = re.search(r"\d+(\.\d+)?", value)
    if not match:
        return None
    return REGISTRY[operator_name].function(float(match.group()))


def run_chamber4(claims_by_domain: dict, operator_name: str,
                 num_samples: int = 10, seed: int = 42) -> list:
    """
    claims_by_domain: dict mapping domain_name -> list of claim strings
        (each claim string should contain at least one numeric value).
    operator_name: REQUIRED. Must name a REGISTRY operator. v0.1 defaulted
        to mod-13 silently; v0.2 forces the caller to choose and defend it.
    num_samples: number of random domain-pair trials to run.
    seed: fixed seed for reproducibility of the random sampling itself.
    """
    if operator_name not in REGISTRY:
        raise ValueError(
            f"Unknown operator '{operator_name}'. Choose from REGISTRY: "
            f"{sorted(REGISTRY)}")
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
            reason = ("Same function applied to both domains' quantities with "
                      "matching output. SYNTACTIC consistency only — this is "
                      "not evidence the domains share a mechanism.")
        else:
            flag = ConsistencyFlag.INCONSISTENT
            reason = (f"Operator produced divergent results ({res_a} vs {res_b}); "
                      f"mapping may require special-casing = cherry-pick risk.")

        results.append(Chamber4Result(
            claim_pair=f"{dom_a}<->{dom_b}",
            domain_a=dom_a,
            domain_b=dom_b,
            operator_applied=operator_name,
            result_a=str(res_a), result_b=str(res_b),
            flag=flag.value, reason=reason
        ))

    return results


if __name__ == "__main__":
    claims_by_domain = {
        "social_networks": ["network size 100 nodes", "network size 50 nodes"],
        "mesh_networks": ["network size 100 nodes", "network size 25 nodes"],
    }
    for r in run_chamber4(claims_by_domain, "metcalfe_scaling", num_samples=4):
        print(r.claim_pair, "->", r.flag, f"({r.result_a} vs {r.result_b})")
