"""
RGH Chamber 1: External Measurement Gate
Reality Grounding Harness — Chamber 1 of 5 (v0.2)

Purpose: Determine whether a claim makes contact with something measurable
in the physical world, independent of framework-specific vocabulary.

v0.2 changes:
- Token-based keyword matching (word boundaries). v0.1 used substring
  matching, which classified "rapid" as an engineering/API claim because
  it contains "api".
- A claim is MEASURABLE_QUANTIFIED only if it names a quantity with a
  unit or scale (%, times, m/s, ...). Measurable language without a
  quantity is MEASURABLE_UNTESTED.
- Change-words (increase/decrease/percent/times/...) are measurable
  markers, so quantitative claims like "3-7x increase in pattern
  recognition" pass the gate they were built for.

Output states (fail-closed philosophy):
- MEASURABLE_QUANTIFIED
- MEASURABLE_UNTESTED
- UNMEASURABLE
- NOT_A_MEASURABLE_CLAIM
"""

import re
from dataclasses import dataclass, asdict
from enum import Enum


class MeasurabilityFlag(Enum):
    MEASURABLE_QUANTIFIED = "MEASURABLE_QUANTIFIED"
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
    "measure", "measures", "measured", "measuring", "measurable",
    "measurement",
    "data", "experiment", "predict", "predicts", "value", "constant",
    "frequency", "signal", "radar", "seismic", "weather", "radio",
    "energy", "mass", "velocity", "temperature", "voltage",
    # v0.2: change-words, so quantitative claims pass the gate
    "increase", "increases", "increased", "decrease", "decreases",
    "decreased", "percent", "change", "changes", "changed", "times",
    "fold", "higher", "lower", "greater", "reduction", "improvement",
]

UNMEASURABLE_KEYWORDS = [
    "belief", "myth", "spirit", "soul", "destiny", "sacred", "divine",
    "essence", "meaning", "purpose", "truth requires no proof",
]

ENGINEERING_KEYWORDS = [
    "pipeline", "transpiler", "spec", "cli", "json", "encode", "decode",
    "normalize", "packet", "monitor", "architecture", "protocol design",
    "schema", "api", "function", "module",
]

# A quantity: number followed by a unit or scale word, or an ad-hoc
# "<word> units" scale (e.g. "7 resonance units", "5 arbitrary units").
QUANTITY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(%|percent|times|fold"
    r"|m/s|km/h|hz|khz|mhz|ghz|j\b|kj\b|w\b|kw\b|v\b|kv\b|a\b|ma\b"
    r"|k\b|kg\b|g\b|mg\b|s\b|ms\b|us\b|ns\b|min\b|hr\b|day\b"
    r"|m\b|km\b|cm\b|mm\b|nm\b|n\b|kn\b|pa\b|kpa\b|t\b|ev\b|kev\b"
    r"|mol\b|cd\b|lx\b|db\b"
    r"|\bx\b"  # bare "3x" style multiplier
    r"|[a-z]+\s+units?)",
    re.IGNORECASE,
)


def _token_hits(text: str, keywords: list) -> list:
    """Token-based keyword matching: whole words only, never substrings.

    v0.1 used `kw in text`, so "rapid" matched "api" and "signaling"
    matched "signal". That is fixed here.
    """
    hits = []
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", text):
            hits.append(kw)
    return hits


@dataclass
class ClaimResult:
    claim_id: str
    source_doc: str
    original_text: str
    null_vocab_text: str
    flag: str
    reason: str
    contradicts_known_constant: bool
    quantity: str = ""  # e.g. "5 %" or "299792458 m/s", "" if none detected


def strip_framework_vocab(text: str) -> str:
    """Replace framework-specific terms with plain-language equivalents."""
    result = text.lower()
    for term, replacement in FRAMEWORK_VOCAB.items():
        result = re.sub(re.escape(term), replacement, result)
    return result


def extract_quantity(text: str) -> str:
    """Return the first 'number + unit' match, or '' if none."""
    m = QUANTITY_RE.search(text)
    if not m:
        return ""
    unit = m.group(2)
    if unit.lower() == "x":
        unit = "times"
    return f"{m.group(1)} {unit}"


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
    engineering-only > quantified measurable > measurable language >
    untranslatable vocab-only > not a claim.
    """
    lower_text = text.lower()
    null_text = strip_framework_vocab(text)
    measurable_hits = _token_hits(null_text, MEASURABLE_KEYWORDS)
    unmeasurable_hits = _token_hits(null_text, UNMEASURABLE_KEYWORDS)
    engineering_hits = _token_hits(null_text, ENGINEERING_KEYWORDS)
    contradicts = check_constant_contradiction(null_text)
    vocab_terms_found = [t for t in FRAMEWORK_VOCAB if t in lower_text]
    quantity = extract_quantity(null_text)

    if unmeasurable_hits:
        flag = MeasurabilityFlag.UNMEASURABLE
        reason = (f"Claim contains mythic/unfalsifiable language "
                  f"({', '.join(unmeasurable_hits)}) that overrides any measurable "
                  f"keywords present; fails closed.")
    elif contradicts:
        flag = MeasurabilityFlag.UNMEASURABLE
        reason = ("Claim translates to a measurable statement but contradicts an "
                  "established physical constant.")
    elif engineering_hits and not measurable_hits:
        flag = MeasurabilityFlag.NOT_A_MEASURABLE_CLAIM
        reason = ("Claim describes engineering/architecture specification, not an "
                  "empirical claim about physical reality.")
    elif measurable_hits and quantity:
        flag = MeasurabilityFlag.MEASURABLE_QUANTIFIED
        reason = (f"Claim names a quantity ({quantity}) with measurable language "
                  f"({', '.join(measurable_hits[:3])}); ready for a falsifiability test.")
    elif measurable_hits:
        flag = MeasurabilityFlag.MEASURABLE_UNTESTED
        reason = ("Claim uses measurable language but names no quantity; "
                  "testable only once a quantity is specified.")
    elif vocab_terms_found:
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
        contradicts_known_constant=contradicts,
        quantity=quantity,
    )


def run_chamber1(claims: list) -> list:
    """claims: list of (claim_id, source_doc, text) tuples."""
    return [classify_claim(cid, doc, text) for cid, doc, text in claims]


if __name__ == "__main__":
    sample_claims = [
        ("C001", "example.md", "The system aggregates public radio and radar data."),
        ("C002", "example.md", "Pattern recognition increases 3 to 7 times."),
        ("C003", "example.md", "Rapid amplitude increase as damping reaches zero."),
    ]
    for r in run_chamber1(sample_claims):
        print(r.claim_id, "->", r.flag, "| qty:", r.quantity or "-")
        print("   ", r.reason[:100])
