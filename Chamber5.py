"""
RGH Chamber 5: Synthesis and Constraint Layer
Reality Grounding Harness — Final Synthesis (v0.2)

Purpose: Act as the final orchestrator. It imports the results of Chambers
1-4, enforces thermodynamic and logical constraints, and produces a
'Synthesis' verdict on the validity of the framework's claims.

v0.2 changes:
- The thermodynamic gate no longer hardcodes a field gradient
  (v0.1: field_gradient = 1.0e10, "Needs to be derived from claim") or a
  magic threshold. check_thermodynamics extracts what the claim actually
  asserts: explicit free-energy / over-unity / perpetual-motion language
  is a THERMODYNAMIC_VIOLATION; a named energy quantity with a source is
  THERMODYNAMIC_OK; anything else is CANNOT_ASSESS — an honest
  admission, not a hardcoded pass.
- synthesize() now actually emits the verdicts the README always
  advertised: PHYSICALLY_GROUNDED requires a Chamber 2 SURVIVED with
  evidence; NEEDS_EVIDENCE covers falsifiable-but-untested claims;
  CLAIM_FALSIFIED, THERMODYNAMIC_VIOLATION, LOGICAL_INCONSISTENCY and
  UNFALSIFIABLE_ROUTED cover the failure modes.

Output states:
- PHYSICALLY_GROUNDED
- NEEDS_EVIDENCE
- CLAIM_FALSIFIED
- UNFALSIFIABLE_ROUTED
- REPLICATION_FAILED
- LOGICAL_INCONSISTENCY
- THERMODYNAMIC_VIOLATION
"""

import re
from dataclasses import dataclass
from Chamber1 import ClaimResult
from Chamber2 import Chamber2Result
from Chamber4 import Chamber4Result


@dataclass
class SynthesisVerdict:
    status: str
    summary: str
    action_items: list


# Language that asserts net energy creation without a source.
FREE_ENERGY_RE = re.compile(
    r"\b(free energy|over-unity|overunity|perpetual motion|"
    r"energy from nothing|creates energy|violates?\s+(the\s+)?(first|second)\s+law"
    r"|infinite (energy|power) (source|output))\b",
    re.IGNORECASE,
)

# A named energy quantity (number + energy unit).
ENERGY_QTY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(j\b|kj\b|mj\b|gj\b|wh\b|kwh\b|mwh\b|ev\b|kev\b|mev\b|gev\b)",
    re.IGNORECASE,
)


def check_thermodynamics(claim_text: str):
    """
    Enforce the Thermodynamic Guardrail honestly.
    Returns (status, reason) where status is one of
    THERMODYNAMIC_VIOLATION / THERMODYNAMIC_OK / CANNOT_ASSESS.
    v0.1 hardcoded a gradient and a magic number; v0.2 derives the
    verdict from what the claim actually asserts, and admits when it
    cannot assess.
    """
    if FREE_ENERGY_RE.search(claim_text):
        return ("THERMODYNAMIC_VIOLATION",
                "Claim asserts net energy creation without a named source; "
                "violates the first law as stated.")
    if ENERGY_QTY_RE.search(claim_text):
        return ("THERMODYNAMIC_OK",
                "Claim names an energy quantity; no free-energy assertion "
                "detected. (Budgeting the source is the experimenter's job.)")
    return ("CANNOT_ASSESS",
            "Claim asserts no energy quantity and no free-energy mechanism; "
            "thermodynamic gate cannot assess it.")


class RGH_SynthesisEngine:
    def __init__(self, chamber1_data, chamber2_data, chamber4_data,
                 claim_texts: dict = None):
        self.c1 = chamber1_data
        self.c2 = chamber2_data
        self.c4 = chamber4_data
        self.texts = claim_texts or {}

    def synthesize(self) -> SynthesisVerdict:
        """Aggregate chamber results into one verdict. Fail-closed:
        the worst finding sets the status."""
        action_items = []

        # Physics gate: thermodynamic violations in any claim text.
        for res in self.c1:
            text = self.texts.get(res.claim_id, res.original_text)
            status, reason = check_thermodynamics(text)
            if status == "THERMODYNAMIC_VIOLATION":
                return SynthesisVerdict(
                    status="THERMODYNAMIC_VIOLATION",
                    summary=f"Claim {res.claim_id}: {reason}",
                    action_items=[f"Drop or re-derive claim {res.claim_id} with "
                                  f"an explicit energy budget."],
                )

        # Logic gate: Chamber 4 inconsistencies.
        for res in self.c4:
            if "INCONSISTENT" in res.flag:
                action_items.append(
                    f"Logic failure in domain pair {res.claim_pair} "
                    f"({res.operator_applied}): {res.reason}")

        # Falsifiability gate.
        falsified = [r.claim_id for r in self.c2
                     if r.flag == "FALSIFIABLE_AND_FAILED"]
        unfalsifiable = [r.claim_id for r in self.c2
                         if r.flag == "UNFALSIFIABLE"]
        survived = [r.claim_id for r in self.c2
                    if r.flag == "FALSIFIABLE_AND_SURVIVED"]
        pending = [r.claim_id for r in self.c2 if r.flag == "FALSIFIABLE"]

        if falsified:
            return SynthesisVerdict(
                status="CLAIM_FALSIFIED",
                summary=f"Claims falsified by evidence: {falsified}.",
                action_items=[f"Retire or revise claim {c}." for c in falsified]
                + action_items,
            )
        if action_items:  # chamber-4 inconsistencies collected above
            return SynthesisVerdict(
                status="LOGICAL_INCONSISTENCY",
                summary=f"{len(action_items)} cross-domain inconsistency(ies).",
                action_items=action_items,
            )
        if unfalsifiable:
            return SynthesisVerdict(
                status="UNFALSIFIABLE_ROUTED",
                summary=(f"Claims with no disconfirming prediction, routed out "
                         f"of the empirical track: {unfalsifiable}."),
                action_items=[f"Reformulate claim {c} with a quantity and "
                              f"comparison, or label it metaphysical." for c in unfalsifiable]
                + ([f"Evidence-pending claims: {pending}."] if pending else []),
            )
        if survived and not pending:
            return SynthesisVerdict(
                status="PHYSICALLY_GROUNDED",
                summary=(f"All surviving claims passed with evidence: "
                         f"{survived}."),
                action_items=["Proceed to independent replication (Chamber 3)."],
            )
        return SynthesisVerdict(
            status="NEEDS_EVIDENCE",
            summary=("No failures and no violations, but no claim has "
                     "survived against evidence yet. "
                     f"Falsifiable-pending: {pending}."),
            action_items=["Attach measurements via Chamber 2 evidence_by_id, "
                          "then re-run synthesis."],
        )


if __name__ == "__main__":
    # Example execution flow
    print("RGH Chamber 5 Synthesis: Finalizing Reality Audit...")
    # This module is called by your CoreEngine.tick()
    # as the final filter before signal output.
