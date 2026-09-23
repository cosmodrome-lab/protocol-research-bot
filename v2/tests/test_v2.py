#!/usr/bin/env python3
"""24 V2 tests + production negatives. CONTRACT_V1 not modified."""
from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "v2" / "engine"))
from validate_profile import errors as v1_errors  # noqa: E402
from validate_v2 import load, v2_enabled, v2_errors  # noqa: E402

HYPE_V1 = ROOT / "profiles" / "HYPE" / "PROFILE.r3.yaml"
AAVE_V1 = ROOT / "profiles" / "AAVE" / "PROFILE.r1.yaml"
HYPE_V2 = ROOT / "v2" / "profiles" / "BOT-HYPE-001.v2.yaml"
AAVE_V2 = ROOT / "v2" / "profiles" / "BOT-AAVE-001.v2.yaml"
HYPE_REG = ROOT / "v2" / "objects" / "HYPE.yaml"
AAVE_REG = ROOT / "v2" / "objects" / "AAVE.yaml"
CONTRACT = ROOT / "CONTRACT_V1.yaml"


def T(name, cond, detail=""):
    return {"name": name, "result": "PASS" if cond else "FAIL", "detail": detail}


def run() -> list[dict]:
    out = []
    h1, a1 = load(HYPE_V1), load(AAVE_V1)
    h2, a2 = load(HYPE_V2), load(AAVE_V2)
    hr, ar = load(HYPE_REG), load(AAVE_REG)

    out.append(T("T01_v1_hype_valid", not v1_errors(h1), str(v1_errors(h1)[:2])))
    out.append(T("T02_v1_aave_valid", not v1_errors(a1), str(v1_errors(a1)[:2])))
    out.append(T("T03_v2_hype_valid", not v2_errors(h2, hr), str(v2_errors(h2, hr)[:3])))
    out.append(T("T04_v2_aave_valid", not v2_errors(a2, ar), str(v2_errors(a2, ar)[:3])))
    out.append(T("T05_v1_profile_v2_disabled", not v2_enabled(h1)))
    out.append(T("T06_v1_aave_v2_disabled", not v2_enabled(a1)))
    out.append(T("T07_v2_enabled_hype", v2_enabled(h2)))
    out.append(T("T08_v2_enabled_aave", v2_enabled(a2)))

    bad = copy.deepcopy(h2)
    bad["layers"]["smart_contracts"]["findings"][0].pop("object_id", None)
    out.append(T("T09_finding_without_object_id_fail", any("missing object_id" in e for e in v2_errors(bad, hr))))

    bad = copy.deepcopy(a2)
    labs_f = bad["layers"]["founders_management_entities"]["findings"][0]
    labs_f["claim"] = "Labs deployed bytecode pool_impl is the protocol deployment"
    labs_f.pop("related_object", None)
    labs_f.pop("source_finding_ids", None)
    out.append(T("T10_labs_to_protocol_without_link_fail", any("Labs statement" in e for e in v2_errors(bad, ar))))

    out.append(T("T11_hype_bytecode_not_proven", h2["bytecode_audit"][0]["result"] == "NOT_PROVEN"))
    out.append(T("T12_aave_bytecode_partial", a2["bytecode_audit"][0]["result"] == "PARTIAL"))
    out.append(T("T13_audit_page_not_auto_proven", h2["bytecode_audit"][0]["explicit_linkage"] == "NO"))
    out.append(T("T14_aave_impl_has_real_hash", len(a2["bytecode_audit"][0]["runtime_bytecode_sha256"]) == 64))
    out.append(T("T15_no_test_hash_token", "deadbeef" not in str(h2["bytecode_audit"]) and "test_hash" not in str(a2["bytecode_audit"])))
    out.append(T("T16_same_as_of_hype", h2["bytecode_audit"][0]["as_of"] == "2026-09-23"))
    out.append(T("T17_same_as_of_aave", a2["bytecode_audit"][0]["as_of"] == "2026-09-23"))

    bad = copy.deepcopy(h2)
    bad["incidents"][0].pop("event_id", None)
    out.append(T("T18_incident_without_event_id_fail", any("missing event_id" in e for e in v2_errors(bad, hr))))
    bad = copy.deepcopy(a2)
    bad["incidents"][0].pop("who_could_do_it", None)
    out.append(T("T19_incident_without_who_fail", any("who_could_do_it" in e for e in v2_errors(bad, ar))))
    out.append(T("T20_hype_incident_has_object", bool(h2["incidents"][0].get("object_id"))))
    out.append(T("T21_aave_incident_has_event", bool(a2["incidents"][0].get("event_id"))))
    out.append(T("T22_v2_disabled_on_v1", not v2_enabled(h1)))
    out.append(T("T23_hype_all_findings_have_object", all(f.get("object_id") for b in h2["layers"].values() for f in b.get("findings") or [])))
    out.append(T("T24_aave_all_findings_have_object", all(f.get("object_id") for b in a2["layers"].values() for f in b.get("findings") or [])))
    return out


def production_negatives():
    h2 = load(HYPE_V2)
    hr = load(HYPE_REG)
    a2 = load(AAVE_V2)
    ar = load(AAVE_REG)
    out = []
    bad = copy.deepcopy(h2)
    bad["layers"]["tokenomics"]["findings"][0]["claim"] = "Buy HYPE sell market undervalued"
    out.append(T("N01_buy_sell", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    bad["fif_dimensions_questions_only"] = {"letter_grade": "A"}
    out.append(T("N02_letter_grade", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    for f in bad["layers"]["disclosure_quality"]["findings"]:
        if f.get("epistemology") == "OBSERVED":
            f["evidence_status"] = "SECONDARY"
    out.append(T("N03_observed_secondary", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    for f in bad["layers"]["disclosure_quality"]["findings"]:
        if f.get("epistemology") == "OBSERVED":
            f["locator"] = "https://medium.com/@Cosmodrome-eng./x"
    out.append(T("N04_medium_observed", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    if bad["layers"]["weaknesses"]["findings"]:
        bad["layers"]["weaknesses"]["findings"][0]["source_finding_ids"] = []
    out.append(T("N05_summary_no_sources", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    bad["layers"]["jurisdiction_legal"] = {"findings": []}
    bad["unknowns"] = [u for u in bad["unknowns"] if u["layer"] != "jurisdiction_legal"]
    out.append(T("N06_missing_axis", bool(v1_errors(bad))))
    bad = copy.deepcopy(h2)
    bad["layers"]["smart_contracts"]["findings"][0].pop("object_id")
    out.append(T("N07_v2_no_object", bool(v2_errors(bad, hr))))
    bad = copy.deepcopy(a2)
    bad["incidents"][0].pop("event_id")
    out.append(T("N08_v2_no_event_id", bool(v2_errors(bad, ar))))
    return out


if __name__ == "__main__":
    rows = run() + production_negatives()
    fails = [r for r in rows if r["result"] != "PASS"]
    for r in rows:
        print(f"{r['result']} {r['name']} {r.get('detail','')}")
    print(f"TOTAL={len(rows)} FAIL={len(fails)}")
    sys.exit(0 if not fails else 1)
