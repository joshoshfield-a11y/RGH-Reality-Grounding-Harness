"""
RGH Chamber 1: External Measurement Gate
Reality Grounding Harness — Chamber 1 of 4

Purpose: Determine whether a claim makes contact with something measurable
in the physical world, independent of framework-specific vocabulary.

Output states (fail-closed philosophy):
- MEASURABLE_CONFIRMED
- MEASURABLE_UNTESTED
- UNMEASURABLE
- NOT_A_MEASURABLE_CLAIM
"""

import re
from dataclasses import dataclass, asdict
from enum import Enum


class MeasurabilityFlag(Enum):
    MEASURABLE_CONFIRMED = "MEASURABLE_CONFIRMED"
    MEASURABLE_UNTESTED = "MEASURABLE_UNTESTED"
    UNMEASURABLE = "UNMEASURABLE"
    NOT_A_MEASURABLE_CLAIM = "NOT_A_MEASURABLE_CLAIM"


# Map framework-specific vocabulary to plain, null-vocabulary equivalents.
# Extend this dictionary as new framework terms are introduced.
FRAMEWORK_VOCAB = {
    "prime pulse": "signal propagation event",
    "triadic state": "three-valued state variable",
    "13-layer context": "13-parameter context vector",
    "base-13": "modulo-13 numeral system",
    "dodecahedron": "12-faced polyhedron",
    "living core": "self-sustaining data process",
    "isomorphism": "structure-preserving mapping",
    "universal isomorphism": "structure-preserving mapping across all tested domains",
    "tree of life": "hierarchical symbolic taxonomy",
    "quantum static": "background electromagnetic noise",
}

# Known physical constants used to check for hard contradictions.
PHYSICS_CONSTANTS = {
    "speed of light": 299792458,          # m/s
    "gravitational constant": 6.674e-11,  # m^3 kg^-1 s^-2
    "planck constant": 6.626e-34,         # J*s
}

MEASURABLE_KEYWORDS = [
    "measure", "data", "experiment", "predict", "value", "constant",
    "frequency", "signal", "radar", "seismic", "weather", "radio",
    "energy", "mass", "velocity", "temperature", "voltage"
]

UNMEASURABLE_KEYWORDS = [
    "belief", "myth", "spirit", "soul", "destiny", "sacred", "divine",
    "essence", "meaning", "purpose", "truth requires no proof"
]

ENGINEERING_KEYWORDS = [
    "pipeline", "transpiler", "spec", "cli", "json", "encode", "decode",
    "normalize", "packet", "monitor", "architecture", "protocol design",
    "schema", "api", "function", "module"
]


@dataclass
class ClaimResult:
    claim_id: str
    source_doc: str
    original_text: str
    null_vocab_text: str
    flag: str
    reason: str
    contradicts_known_constant: bool


def strip_framework_vocab(text: str) -> str:
    """Replace framework-specific terms with plain-language equivalents."""
    result = text.lower()
    for term, replacement in FRAMEWORK_VOCAB.items():
        result = re.sub(re.escape(term), replacement, result)
    return result


def check_constant_contradiction(text: str) -> bool:
    """Return True if the text asserts a value for a known constant that
    deviates from the accepted value by more than 1%."""
    for name, value in PHYSICS_CONSTANTS.items():
        pattern = rf"{name}[^\d]*(\d+(?:\.\d+)?(?:e[+-]?\d+)?)"
        match = re.search(pattern, text.lower())
        if match:
            claimed_value = float(match.group(1))
            if abs(claimed_value - value) / value > 0.01:
                return True
    return False


def classify_claim(claim_id: str, source_doc: str, text: str) -> ClaimResult:
    """
    Classify a single claim into one of four measurability states.
    Priority order (fail-closed): mythic language > constant contradiction >
    engineering-only > measurable > untranslatable vocab-only > not a claim.
    """
    lower_text = text.lower()
    null_text = strip_framework_vocab(text)
    contains_measurable = any(k in null_text for k in MEASURABLE_KEYWORDS)
    contains_unmeasurable = any(k in null_text for k in UNMEASURABLE_KEYWORDS)
    contains_engineering = any(k in null_text for k in ENGINEERING_KEYWORDS)
    contradicts = check_constant_contradiction(null_text)
    vocab_terms_found = [t for t in FRAMEWORK_VOCAB if t in lower_text]

    if contains_unmeasurable:
        flag = MeasurabilityFlag.UNMEASURABLE
        reason = ("Claim contains mythic/unfalsifiable language (belief, sacred, "
                   "essence, etc.) that overrides any measurable keywords present; "
                   "fails closed.")
    elif contradicts:
        flag = MeasurabilityFlag.UNMEASURABLE
        reason = ("Claim translates to a measurable statement but contradicts an "
                   "established physical constant.")
    elif contains_engineering and not contains_measurable:
        flag = MeasurabilityFlag.NOT_A_MEASURABLE_CLAIM
        reason = ("Claim describes engineering/architecture specification, not an "
                   "empirical claim about physical reality.")
    elif contains_measurable:
        flag = MeasurabilityFlag.MEASURABLE_UNTESTED
        reason = ("Claim translates to a measurable statement; no confirming "
                   "dataset checked yet in this pass.")
    elif len(vocab_terms_found) > 0:
        flag = MeasurabilityFlag.UNMEASURABLE
        reason = ("Claim relies entirely on framework-specific vocabulary with no "
                   "measurable or engineering referent after translation.")
    else:
        flag = MeasurabilityFlag.NOT_A_MEASURABLE_CLAIM
        reason = ("No measurable, mythic, or engineering markers detected; claim "
                   "does not make a testable assertion in this pass.")

    return ClaimResult(
        claim_id=claim_id,
        source_doc=source_doc,
        original_text=text,
        null_vocab_text=null_text,
        flag=flag.value,
        reason=reason,
        contradicts_known_constant=contradicts
    )


def run_chamber1(claims: list) -> list:
    """claims: list of (claim_id, source_doc, text) tuples."""
    return [classify_claim(cid, doc, text) for cid, doc, text in claims]


if __name__ == "__main__":
    import pandas as pd
    sample_claims = [
        ("C001", "example.md", "The system aggregates public radio and radar data."),
    ]
    results = run_chamber1(sample_claims)
    df = pd.DataFrame([asdict(r) for r in results])
    print(df.to_string(index=False))