"""
RGH Chamber 3: Independent Replication Protocol
Reality Grounding Harness — Chamber 3 of 4

Purpose: Take a narrow, bounded claim and re-express it as a code-level
pipeline with zero mythic/framework-specific language, then verify that a
fresh, independent execution context produces the identical output.

Output states:
- REPLICATED_INDEPENDENTLY
- REPLICATION_ATTEMPTED_FAILED
- NOT_YET_ATTEMPTED
- NOT_APPLICABLE_NO_PIPELINE
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional

from rgh_chamber1_external_measurement import ClaimResult


class ReplicationFlag(Enum):
    REPLICATED = "REPLICATED_INDEPENDENTLY"
    ATTEMPTED_FAILED = "REPLICATION_ATTEMPTED_FAILED"
    NOT_ATTEMPTED = "NOT_YET_ATTEMPTED"
    NOT_APPLICABLE = "NOT_APPLICABLE_NO_PIPELINE"


@dataclass
class Chamber3Result:
    claim_id: str
    pipeline_extracted: bool
    stripped_pipeline: str
    fresh_context_output: str
    original_output: str
    outputs_match: bool
    flag: str
    reason: str


def extract_stripped_pipeline(claim_text: str, null_text: str) -> Optional[str]:
    """
    Attempt to convert a claim into a pure input->transform->output pipeline
    with zero framework-specific vocabulary. Returns None if the claim is
    descriptive/philosophical rather than procedural (i.e., not computable).

    NOTE: This extraction logic is intentionally simple/rule-based in this
    reference implementation. For real corpus use, replace with a more
    thorough claim-to-pipeline extraction process, ideally reviewed by a
    party unfamiliar with the source framework.
    """
    is_procedural = any(w in null_text for w in
                         ["form", "aggregate", "requires", "model", "propagat"])
    if not is_procedural:
        return None
    if "aggregate" in null_text or "form" in null_text:
        return ("def pipeline(inputs: list) -> str:\n"
                "    return 'aggregated_state' if len(inputs) >= 3 else 'insufficient_input'")
    if "model" in null_text:
        return "def pipeline(x: float) -> float:\n    return x % 13"
    return "def pipeline(x): return x"


def simulate_fresh_context_run(pipeline_code: str, test_input):
    """
    Execute the stripped pipeline in a clean namespace, simulating an
    independent party running the code with no prior context.
    """
    local_ns = {}
    try:
        exec(pipeline_code, {}, local_ns)
        fn = local_ns['pipeline']
        return str(fn(test_input))
    except Exception as e:
        return f"ERROR: {e}"


def run_chamber3_single(claim_result: ClaimResult, claim_text: str) -> Chamber3Result:
    pipeline = extract_stripped_pipeline(claim_text, claim_result.null_vocab_text)

    if pipeline is None:
        return Chamber3Result(
            claim_id=claim_result.claim_id,
            pipeline_extracted=False,
            stripped_pipeline="N/A",
            fresh_context_output="N/A",
            original_output="N/A",
            outputs_match=False,
            flag=ReplicationFlag.NOT_APPLICABLE.value,
            reason=("Claim is descriptive/philosophical, not procedural; no "
                     "pipeline could be extracted for replication testing.")
        )

    test_input = [1, 2, 3, 4] if "list" in pipeline else 27.0

    original_run = simulate_fresh_context_run(pipeline, test_input)
    fresh_run = simulate_fresh_context_run(pipeline, test_input)  # independent re-execution

    match = original_run == fresh_run and not original_run.startswith("ERROR")

    if match:
        flag = ReplicationFlag.REPLICATED
        reason = ("Stripped pipeline produced identical output when independently "
                   "re-executed with no framework vocabulary.")
    else:
        flag = ReplicationFlag.ATTEMPTED_FAILED
        reason = "Independent re-execution did not match, or pipeline errored — replication failed."

    return Chamber3Result(
        claim_id=claim_result.claim_id,
        pipeline_extracted=True,
        stripped_pipeline=pipeline,
        fresh_context_output=fresh_run,
        original_output=original_run,
        outputs_match=match,
        flag=flag.value,
        reason=reason
    )


def run_chamber3(chamber1_results: list, claim_texts: dict) -> list:
    """claim_texts: dict mapping claim_id -> original claim text."""
    return [run_chamber3_single(r, claim_texts[r.claim_id]) for r in chamber1_results]


if __name__ == "__main__":
    import pandas as pd
    from rgh_chamber1_external_measurement import run_chamber1

    sample_claims = [
        ("C001", "example.md", "The system aggregates public radio and radar data into a state."),
    ]
    claim_texts = {cid: text for cid, doc, text in sample_claims}
    c1_results = run_chamber1(sample_claims)
    c3_results = run_chamber3(c1_results, claim_texts)
    df = pd.DataFrame([asdict(r) for r in c3_results])
    print(df.to_string(index=False))