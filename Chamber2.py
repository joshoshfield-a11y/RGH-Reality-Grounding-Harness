"""
RGH Chamber 2: Falsifiability Stress Test
Reality Grounding Harness — Chamber 2 of 5 (v0.2)

Purpose: For every claim that passes Chamber 1 as measurable, generate the
strongest possible disconfirming prediction and check whether the framework
has any escape hatch.

v0.2 changes:
- The v0.1 "has a digit -> falsifiable" heuristic is gone. A claim is
  falsifiable when it names a quantity with a unit/scale plus a
  comparison (more than / less than / increases / decreases), or a
  causal intervention that can be withheld. The adversarial prediction
  cites the actual quantity instead of a generic sentence.
- No more auto-SURVIVED. A claim that is falsifiable but has no
  evidence attached is FALSIFIABLE (test constructed, verdict pending),
  not FALSIFIABLE_AND_SURVIVED. SURVIVED/FAILED require evidence passed
  as evidence_by_id={claim_id: {"measured": float}}.

Output states:
- FALSIFIABLE
- FALSIFIABLE_AND_SURVIVED
- FALSIFIABLE_AND_FAILED
- UNFALSIFIABLE
- NOT_APPLICABLE_CHAMBER1_GATE
"""

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional

from Chamber1 import ClaimResult, MeasurabilityFlag


class FalsifiabilityFlag(Enum):
    FALSIFIABLE = "FALSIFIABLE"
    SURVIVED = "FALSIFIABLE_AND_SURVIVED"
    FAILED = "FALSIFIABLE_AND_FAILED"
    UNFALSIFIABLE = "UNFALSIFIABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE_CHAMBER1_GATE"


# Words that turn a quantity into a comparison (a real falsifier needs one).
COMPARATOR_RE = re.compile(
    r"\b(more than|less than|greater than|fewer than|at least|at most|"
    r"increases?|decreases?|improves?|reduces?|exceeds?|above|below|"
    r"over|under|>|<|>=|<=)\b",
    re.IGNORECASE,
)

# Causal verbs whose effect can be tested by withholding the cause.
CAUSAL_RE = re.compile(
    r"\b(causes|produces|generates|requires|depends on|drives|triggers)\b",
    re.IGNORECASE,
)

GATE_FLAGS = (
    MeasurabilityFlag.MEASURABLE_QUANTIFIED.value,
    MeasurabilityFlag.MEASURABLE_UNTESTED.value,
)


@dataclass
class Chamber2Result:
    claim_id: str
    chamber1_flag: str
    adversarial_prediction: str
    test_outcome: str
    flag: str
    reason: str


def generate_adversarial_prediction(claim_result: ClaimResult) -> Optional[str]:
    """
    Generate the strongest disconfirming prediction possible for a claim.
    Returns None if no disconfirming prediction can be constructed, which
    itself is a meaningful and valid result (= unfalsifiable).
    """
    text = claim_result.null_vocab_text
    quantity = claim_result.quantity

    if quantity and COMPARATOR_RE.search(text):
        comp = COMPARATOR_RE.search(text).group(1)
        return (f"Measure the quantity ({quantity}); the claim fails if the "
                f"observed value does not satisfy '{comp} {quantity}'.")
    if quantity:
        return (f"Measure the quantity ({quantity}); the claim fails if an "
                f"independent measurement disagrees beyond stated tolerance.")
    if CAUSAL_RE.search(text):
        return ("Withhold/remove the stated cause while holding other "
                "conditions fixed; the claim fails if the effect persists.")
    return None


def run_chamber2_single(claim_result: ClaimResult,
                        evidence: Optional[dict] = None) -> Chamber2Result:
    """
    Run the falsifiability test on a single Chamber 1 result.
    evidence: optional {"measured": float} — an independent measurement of
    the claimed quantity. Without evidence, a falsifiable claim is
    FALSIFIABLE (verdict pending), never auto-SURVIVED.
    """
    if claim_result.flag not in GATE_FLAGS:
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction="N/A",
            test_outcome="N/A",
            flag=FalsifiabilityFlag.NOT_APPLICABLE.value,
            reason=("Chamber 1 did not flag this claim as measurable; Chamber 2 "
                    "only runs on MEASURABLE_QUANTIFIED/MEASURABLE_UNTESTED claims.")
        )

    prediction = generate_adversarial_prediction(claim_result)

    if prediction is None:
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction="NONE_CONSTRUCTIBLE",
            test_outcome="N/A",
            flag=FalsifiabilityFlag.UNFALSIFIABLE.value,
            reason=("No disconfirming experiment could be constructed from this "
                    "claim's structure: no quantified comparison and no "
                    "withholdable cause. Passing Chamber 1 does not guarantee "
                    "falsifiability.")
        )

    if claim_result.contradicts_known_constant:
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction=prediction,
            test_outcome="FAILED — contradicts measured reality",
            flag=FalsifiabilityFlag.FAILED.value,
            reason="Claim contradicts an established physical constant.",
        )

    if evidence and "measured" in evidence and claim_result.quantity:
        claimed_num = float(re.match(r"[\d.]+", claim_result.quantity).group())
        measured = float(evidence["measured"])
        tol = float(evidence.get("tolerance", 0.05 * abs(claimed_num) or 1e-9))
        comp_m = COMPARATOR_RE.search(claim_result.null_vocab_text)
        comp = comp_m.group(1).lower() if comp_m else ""
        if any(w in comp for w in ("more than", "greater than", "at least",
                                   "increase", "improve", "exceed", "above", "over")):
            passed = measured >= claimed_num - tol
        elif any(w in comp for w in ("less than", "fewer than", "at most",
                                     "decrease", "reduce", "below", "under")):
            passed = measured <= claimed_num + tol
        else:
            passed = abs(measured - claimed_num) <= tol
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction=prediction,
            test_outcome=(f"EVIDENCE: measured={measured} vs claimed "
                          f"{claim_result.quantity}"),
            flag=(FalsifiabilityFlag.SURVIVED.value if passed
                  else FalsifiabilityFlag.FAILED.value),
            reason="Adversarial test executed against supplied evidence.",
        )

    return Chamber2Result(
        claim_id=claim_result.claim_id,
        chamber1_flag=claim_result.flag,
        adversarial_prediction=prediction,
        test_outcome="PENDING — no evidence attached",
        flag=FalsifiabilityFlag.FALSIFIABLE.value,
        reason=("Disconfirming prediction constructed; verdict awaits an "
                "independent measurement. v0.2 does not auto-survive."),
    )


def run_chamber2(chamber1_results: list,
                 evidence_by_id: Optional[dict] = None) -> list:
    """evidence_by_id: optional {claim_id: {"measured": float, ...}}."""
    evidence_by_id = evidence_by_id or {}
    return [run_chamber2_single(r, evidence_by_id.get(r.claim_id))
            for r in chamber1_results]


if __name__ == "__main__":
    from Chamber1 import run_chamber1

    sample_claims = [
        ("C001", "example.md", "The system aggregates public radio and radar data."),
        ("C002", "example.md", "Heart rate variability increases by more than 5 percent."),
    ]
    c1 = run_chamber1(sample_claims)
    for r in run_chamber2(c1):
        print(r.claim_id, "->", r.flag)
        print("   ", r.adversarial_prediction[:110])
    print("--- with evidence ---")
    for r in run_chamber2(c1, {"C002": {"measured": 7.2}}):
        print(r.claim_id, "->", r.flag, "|", r.test_outcome)
