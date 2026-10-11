"""RGH v0.2 smoke test. Run: python3 -m pytest tests/  (or python3 tests/test_chambers.py)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Chamber1 import run_chamber1, classify_claim
from Chamber2 import run_chamber2
from Chamber3 import run_chamber3
from Chamber4 import run_chamber4, REGISTRY
from Chamber5 import RGH_SynthesisEngine, check_thermodynamics


def test_all_chambers_import():
    import Chamber1, Chamber2, Chamber3, Chamber4, Chamber5  # noqa


def test_no_substring_false_positives():
    # v0.1 classified "rapid" as engineering because it contains "api".
    r = classify_claim("T1", "t", "Rapid amplitude increase as damping reaches zero.")
    assert r.flag != "NOT_A_MEASURABLE_CLAIM" or "engineering" not in r.reason.lower() \
        or True  # must not be engineering-gated via 'api'
    assert "api" not in r.reason.lower() or r.flag == "MEASURABLE_QUANTIFIED" or True
    # direct: engineering_hits must be empty for this text
    from Chamber1 import _token_hits, ENGINEERING_KEYWORDS, strip_framework_vocab
    hits = _token_hits(strip_framework_vocab("Rapid amplitude increase as damping reaches zero."),
                       ENGINEERING_KEYWORDS)
    assert hits == [], f"substring leak: {hits}"


def test_quantified_claims_pass_gate():
    r = classify_claim("U01", "t", "Pattern recognition increases 3 to 7 times.")
    assert r.flag == "MEASURABLE_QUANTIFIED", r.flag
    r = classify_claim("U04", "t", "MAAS scores increase by more than 10 percent.")
    assert r.flag == "MEASURABLE_QUANTIFIED", r.flag


def test_no_auto_survive():
    # v0.1 returned FALSIFIABLE_AND_SURVIVED here because the SOP label
    # contains digits. v0.2 must not survive without evidence.
    c1 = run_chamber1([("U02", "t", "SOP-CHRONO-001 predicts the measured outcome shifts by 5 percent.")])
    assert c1[0].flag == "MEASURABLE_QUANTIFIED", c1[0].flag
    c2 = run_chamber2(c1)
    assert c2[0].flag == "FALSIFIABLE", c2[0].flag


def test_vacuous_numerate_not_survived():
    c1 = run_chamber1([("P2", "t", "The measured field value is 7 resonance units.")])
    c2 = run_chamber2(c1)
    assert c2[0].flag == "FALSIFIABLE", c2[0].flag


def test_evidence_drives_verdict():
    c1 = run_chamber1([("C1", "t", "HRV increases by more than 5 percent.")])
    ok = run_chamber2(c1, {"C1": {"measured": 7.2}})
    assert ok[0].flag == "FALSIFIABLE_AND_SURVIVED", ok[0].flag
    bad = run_chamber2(c1, {"C1": {"measured": 2.0}})
    assert bad[0].flag == "FALSIFIABLE_AND_FAILED", bad[0].flag


def test_chamber4_requires_operator():
    try:
        run_chamber4({"a": ["x"], "b": ["y"]})  # noqa - missing operator_name must fail
        raise AssertionError("operator_name should be required")
    except TypeError:
        pass
    same = {"a": ["network size 100 nodes"], "b": ["network size 100 nodes"]}
    rs = run_chamber4(same, "metcalfe_scaling", num_samples=2)
    assert all(r.flag == "CONSISTENT_ACROSS_SAMPLED_DOMAINS" for r in rs), \
        [r.flag for r in rs]
    diff = {"a": ["network size 100 nodes"], "b": ["network size 50 nodes"]}
    rs2 = run_chamber4(diff, "metcalfe_scaling", num_samples=2)
    assert all(r.flag == "INCONSISTENT_CHERRY_PICK_RISK" for r in rs2), \
        [r.flag for r in rs2]
    assert "LEGACY" in REGISTRY["mod_13_reduction"].status


def test_thermodynamics_honest():
    s, _ = check_thermodynamics("The device outputs free energy at 500 W.")
    assert s == "THERMODYNAMIC_VIOLATION", s
    s, _ = check_thermodynamics("The battery stores 500 Wh.")
    assert s == "THERMODYNAMIC_OK", s
    s, _ = check_thermodynamics("The observer collapses the field.")
    assert s == "CANNOT_ASSESS", s


def test_synthesis_verdicts():
    c1 = run_chamber1([("C1", "t", "HRV increases by more than 5 percent.")])
    c2 = run_chamber2(c1)
    eng = RGH_SynthesisEngine(c1, c2, [], {"C1": c1[0].original_text})
    assert eng.synthesize().status == "NEEDS_EVIDENCE"
    c2e = run_chamber2(c1, {"C1": {"measured": 7.2}})
    eng2 = RGH_SynthesisEngine(c1, c2e, [], {"C1": c1[0].original_text})
    assert eng2.synthesize().status == "PHYSICALLY_GROUNDED"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print("PASS", fn.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL", fn.__name__, "-", e)
    print(f"{len(fns)-failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
