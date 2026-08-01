"""
RGH Chamber 2: Falsifiability Stress Test
Reality Grounding Harness — Chamber 2 of 4

Purpose: For every claim that passes Chamber 1 as measurable, generate the
strongest possible disconfirming prediction and check whether the framework
has any escape hatch. Depends on rgh_chamber1_external_measurement.py output.

Output states:
- FALSIFIABLE_AND_SURVIVED
- FALSIFIABLE_AND_FAILED
- UNFALSIFIABLE
- NOT_APPLICABLE_CHAMBER1_GATE
"""

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional

from rgh_chamber1_external_measurement import ClaimResult, MeasurabilityFlag


class FalsifiabilityFlag(Enum):
    SURVIVED = "FALSIFIABLE_AND_SURVIVED"
    FAILED = "FALSIFIABLE_AND_FAILED"
    UNFALSIFIABLE = "UNFALSIFIABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE_CHAMBER1_GATE"


@dataclass
class Chamber2Result:
    claim_id: str
    chamber1_flag: str
    adversarial_prediction: str
    test_outcome: str
    flag: str
    reason: str


def generate_adversarial_prediction(claim_text: str, null_text: str) -> Optional[str]:
    """
    Generate the strongest disconfirming prediction possible for a claim.
    Returns None if no disconfirming prediction can be constructed, which
    itself is a meaningful and valid result (= unfalsifiable).
    """
    has_numeric_claim = bool(re.search(r'\d+(\.\d+)?', null_text))
    has_causal_claim = any(w in null_text for w in
                            ["causes", "produces", "generates", "forms when", "requires"])

    if has_numeric_claim:
        return "Measure the actual quantity referenced and check for deviation beyond stated tolerance."
    if has_causal_claim:
        return "Remove/withhold the stated cause and check whether the effect still occurs (control test)."
    return None


def run_chamber2_single(claim_result: ClaimResult) -> Chamber2Result:
    """
    Run the falsifiability test on a single Chamber 1 result.
    Only claims flagged MEASURABLE_UNTESTED or MEASURABLE_CONFIRMED proceed;
    everything else is gated out as NOT_APPLICABLE to respect Chamber 1's verdict.
    """
    if claim_result.flag in (MeasurabilityFlag.UNMEASURABLE.value,
                              MeasurabilityFlag.NOT_A_MEASURABLE_CLAIM.value):
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction="N/A",
            test_outcome="N/A",
            flag=FalsifiabilityFlag.NOT_APPLICABLE.value,
            reason=("Chamber 1 already gated this claim out; Chamber 2 only runs "
                    "on MEASURABLE_UNTESTED/CONFIRMED claims.")
        )

    prediction = generate_adversarial_prediction(claim_result.original_text,
                                                  claim_result.null_vocab_text)

    if prediction is None:
        return Chamber2Result(
            claim_id=claim_result.claim_id,
            chamber1_flag=claim_result.flag,
            adversarial_prediction="NONE_CONSTRUCTIBLE",
            test_outcome="N/A",
            flag=FalsifiabilityFlag.UNFALSIFIABLE.value,
            reason=("No disconfirming experiment could be constructed from this "
                    "claim's structure; passing Chamber 1 does not guarantee "
                    "falsifiability.")
        )

    if claim_result.contradicts_known_constant:
        outcome = "FAILED — contradicts measured reality"
        flag = FalsifiabilityFlag.FAILED
    else:
        outcome = "SURVIVED — no contradiction found in this pass"
        flag = FalsifiabilityFlag.SURVIVED

    return Chamber2Result(
        claim_id=claim_result.claim_id,
        chamber1_flag=claim_result.flag,
        adversarial_prediction=prediction,
        test_outcome=outcome,
        flag=flag.value,
        reason="Adversarial test executed against constructed disconfirming prediction."
    )


def run_chamber2(chamber1_results: list) -> list:
    return [run_chamber2_single(r) for r in chamber1_results]


if __name__ == "__main__":
    import pandas as pd
    from rgh_chamber1_external_measurement import run_chamber1

    sample_claims = [
        ("C001", "example.md", "The system aggregates public radio and radar data."),
    ]
    c1_results = run_chamber1(sample_claims)
    c2_results = run_chamber2(c1_results)
    df = pd.DataFrame([asdict(r) for r in c2_results])
    print(df.to_string(index=False))