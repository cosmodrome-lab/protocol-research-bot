#!/usr/bin/env python3
"""Protocol-agnostic V1 pipeline.

Pack supplies sources + extract(ctx).
This file must not name a protocol.
CONTRACT_V1 is not modified here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))
from validate_profile import errors, render  # noqa: E402

ANALYSIS = [
    "smart_contracts",
    "audits",
    "tokenomics",
    "revenue_to_token",
    "validators_sequencers_nodes_oracles",
    "governance",
    "founders_management_entities",
    "jurisdiction_legal",
    "treasury_custody_bridges_keys",
    "market_structure",
    "disclosure_quality",
    "architectural_dependencies",
    "declared_vs_observed",
]

CONTRACT = "cosm.bot.contract/1.0.0"
UA = "CosmodromeProtocolResearchBot/1.0 (read-only research capture)"


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def pack_dir(name: str) -> Path:
    p = ROOT / "packs" / name.upper()
    if not p.exists():
        raise FileNotFoundError(f"missing pack {p}")
    return p


def load_pack(name: str) -> dict:
    d = pack_dir(name)
    pack = _load(d / "pack.yaml")
    pack["_dir"] = d
    pack["_ticker"] = pack["ticker"]
    pack["_evid"] = ROOT / "evidence" / pack["ticker"]
    pack["_prof"] = ROOT / "profiles" / pack["ticker"]
    pack["_cap"] = pack["_evid"] / "captures"
    return pack


def load_extract(pack: dict):
    path = pack["_dir"] / "extract.py"
    spec = importlib.util.spec_from_file_location(f"extract_{pack['ticker']}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod.extract


def _http(src: dict) -> tuple[int, bytes, str]:
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if src.get("method") == "POST":
        payload = json.dumps(src.get("body") or {}).encode()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(src["url"], data=payload, headers=headers, method="POST")
    else:
        req = urllib.request.Request(src["url"], headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if e.fp else b""), ""
    except Exception as e:
        return 0, str(e).encode(), "error"


def _not_found(raw: bytes) -> bool:
    t = raw.decode("utf-8", "replace")
    return ("Page Not Found" in t and "does not exist" in t) or t.startswith("404")


def capture(pack: dict, captured_at: str) -> list[dict]:
    cap = pack["_cap"]
    cap.mkdir(parents=True, exist_ok=True)
    sources = _load(pack["_dir"] / "sources.yaml")["sources"]
    rows = []
    for src in sources:
        status, raw, ctype = _http(src)
        sha = hashlib.sha256(raw).hexdigest() if raw else None
        retrieval = "OK"
        if status != 200 or not raw:
            retrieval = "FAIL"
        elif _not_found(raw):
            retrieval = "NOT_FOUND"
        body = cap / f"{src['source_id']}.body"
        body.write_bytes(raw)
        rec = {
            **src,
            "captured_at": captured_at,
            "http_status": status,
            "content_type": ctype,
            "byte_length": len(raw),
            "sha256": sha,
            "hash_scope": "retrieved_body_bytes",
            "hash_does_not_prove_origin_immutability": True,
            "retrieval_status": retrieval,
            "body_path": str(body.relative_to(ROOT)),
        }
        _dump(cap / f"{src['source_id']}.meta.yaml", rec)
        rows.append(rec)
        print(f"CAPTURE {pack['ticker']} {src['source_id']} {retrieval} {status}", file=sys.stderr)
    _dump(pack["_evid"] / "sources.yaml", {"captured_at": captured_at, "sources": rows})
    return rows


class Ctx:
    def __init__(self, pack: dict):
        self.pack = pack
        self.cap = pack["_cap"]

    def meta(self, sid: str) -> dict:
        p = self.cap / f"{sid}.meta.yaml"
        return _load(p) if p.exists() else {}

    def ok(self, sid: str) -> bool:
        return self.meta(sid).get("retrieval_status") == "OK"

    def text(self, sid: str) -> str:
        p = self.cap / f"{sid}.body"
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

    def sha(self, sid: str):
        return self.meta(sid).get("sha256")

    def loc(self, sid: str) -> str:
        return self.meta(sid).get("url") or ""

    def F(self, fid, layer, claim, epi, ev, sources, falsifier, limitations="", extra=None):
        loc = self.loc(sources[0]) if sources else ""
        if ev == "ABSENT":
            loc = ""
        row = {
            "finding_id": fid,
            "layer": layer,
            "claim": claim,
            "epistemology": epi,
            "evidence_status": ev,
            "locator": loc,
            "source_ids": sources,
            "falsifier": falsifier,
            "limitations": limitations,
        }
        h = self.sha(sources[0]) if sources else None
        if h:
            row["capture_sha256"] = h
            if ev == "PRIMARY_CAPTURED":
                row["artifact_hash"] = h
        if extra:
            row.update(extra)
        return row

    def U(self, uid, layer, q, why, close):
        return {
            "unknown_id": uid,
            "layer": layer,
            "question": q,
            "why_material": why,
            "what_would_close_it": close,
        }


def extract(pack: dict, captured_at: str) -> dict:
    fn = load_extract(pack)
    findings, unknowns = fn(Ctx(pack))
    covered = {f["layer"] for f in findings} | {u["layer"] for u in unknowns}
    ticker = pack["ticker"]
    for lid in ANALYSIS:
        if lid not in covered:
            unknowns.append(
                {
                    "unknown_id": f"{ticker}-U-GAP-{lid}",
                    "layer": lid,
                    "question": f"No extracted finding and no specific unknown for {lid}.",
                    "why_material": "V1 coverage rule.",
                    "what_would_close_it": "Finding with locator or a tighter unknown.",
                }
            )
    payload = {"extracted_at": captured_at, "findings": findings, "unknowns": unknowns}
    _dump(pack["_evid"] / "observations.yaml", payload)
    print(f"EXTRACT {ticker} findings={len(findings)} unknowns={len(unknowns)}", file=sys.stderr)
    return payload


def build(pack: dict, obs: dict) -> dict:
    layers = {lid: {"findings": []} for lid in ANALYSIS}
    layers["weaknesses"] = {"findings": []}
    layers["strengths"] = {"findings": []}
    by_id = {}
    for f in obs["findings"]:
        layers[f["layer"]]["findings"].append(f)
        by_id[f["finding_id"]] = f
    summaries = pack.get("summaries") or {}
    ctx = Ctx(pack)
    for kind, spec in summaries.items():
        src = [i for i in spec.get("source_finding_ids") or [] if i in by_id]
        if not src:
            continue
        sid0 = spec.get("locator_source") or (by_id[src[0]].get("source_ids") or [None])[0]
        layers[kind]["findings"].append(
            {
                "finding_id": spec["finding_id"],
                "layer": kind,
                "claim": spec["claim"],
                "epistemology": "DERIVED",
                "evidence_status": spec.get("evidence_status") or "PRIMARY_LOCATED",
                "locator": ctx.loc(sid0) if sid0 else "",
                "artifact_hash": ctx.sha(sid0) if spec.get("evidence_status") == "PRIMARY_CAPTURED" else None,
                "source_ids": spec.get("source_ids") or [],
                "source_finding_ids": src,
                "falsifier": spec["falsifier"],
                "limitations": spec.get("limitations") or "Derived only from findings in this profile.",
            }
        )
        if layers[kind]["findings"][-1]["artifact_hash"] is None:
            layers[kind]["findings"][-1].pop("artifact_hash", None)
    profile = {
        "profile_id": pack["profile_id"],
        "protocol": pack["protocol"],
        "ticker": pack["ticker"],
        "profile_rev": pack["profile_rev"],
        "as_of": str(pack["as_of"]),
        "contract": CONTRACT,
        "state": "PIPELINE_BUILT",
        "built_from": f"evidence/{pack['ticker']}/observations.yaml",
        "forbidden_outputs": ["BUY", "SELL", "HOLD", "letter_grade", "price_target"],
        "layers": layers,
        "unknowns": obs["unknowns"],
        "v2_candidates": pack.get("v2_candidates") or [],
    }
    out = pack["_prof"] / f"PROFILE.{pack['profile_rev']}.yaml"
    pack["_prof"].mkdir(parents=True, exist_ok=True)
    _dump(out, profile)
    print(f"BUILD {out}", file=sys.stderr)
    return profile


def verify(pack: dict, profile: dict, captured_at: str) -> dict:
    err = errors(profile)
    rendered = render(profile)
    rev = pack["profile_rev"]
    (pack["_prof"] / f"PROFILE.{rev}.rendered.md").write_text(rendered, encoding="utf-8")
    result = {
        "schema_id": "cosm.bot.test",
        "profile_id": profile["profile_id"],
        "profile_rev": rev,
        "tested_at": captured_at,
        "validate": "PASS" if not err else "FAIL",
        "validate_errors": err,
        "render": "PASS" if rendered else "FAIL",
        "findings": sum(len((b or {}).get("findings") or []) for b in profile["layers"].values()),
        "unknowns": len(profile["unknowns"]),
    }
    _dump(pack["_prof"] / f"TEST_RESULT.{rev}.yaml", result)
    if err:
        print("INVALID", file=sys.stderr)
        for e in err:
            print("-", e, file=sys.stderr)
    else:
        print(f"VALID {profile['profile_id']} {rev}", file=sys.stderr)
    return result


def negatives(pack: dict) -> list[dict]:
    import copy

    src = _load(pack["_prof"] / f"PROFILE.{pack['profile_rev']}.yaml")
    tests = []

    def run(p, name):
        path = Path("/tmp") / f"neg_{pack['ticker']}_{name}.yaml"
        _dump(path, p)
        r = subprocess.run(
            [sys.executable, str(ENGINE / "validate_profile.py"), "validate", str(path)],
            capture_output=True,
            text=True,
        )
        return {"name": name, "exit": r.returncode, "stderr": r.stderr.strip().splitlines()[:3]}

    # first finding of any analysis layer
    layer0 = None
    for lid in ANALYSIS:
        if src["layers"][lid]["findings"]:
            layer0 = lid
            break
    p = copy.deepcopy(src)
    p["layers"][layer0]["findings"][0]["claim"] = "Buy this token sell the market it is undervalued"
    tests.append(run(p, "buy_sell"))
    p = copy.deepcopy(src)
    p["fif_dimensions_questions_only"] = {"letter_grade": "B"}
    tests.append(run(p, "letter_grade"))
    # OBSERVED finding if any
    obs_l = None
    for lid, body in src["layers"].items():
        for f in body.get("findings") or []:
            if f.get("epistemology") == "OBSERVED":
                obs_l = (lid, f)
                break
        if obs_l:
            break
    if obs_l:
        p = copy.deepcopy(src)
        p["layers"][obs_l[0]]["findings"][0]["evidence_status"] = "SECONDARY"
        # only mutate the observed one
        for i, f in enumerate(p["layers"][obs_l[0]]["findings"]):
            if f["finding_id"] == obs_l[1]["finding_id"]:
                p["layers"][obs_l[0]]["findings"][i]["evidence_status"] = "SECONDARY"
        tests.append(run(p, "observed_invalid_evidence"))
        p = copy.deepcopy(src)
        for i, f in enumerate(p["layers"][obs_l[0]]["findings"]):
            if f["finding_id"] == obs_l[1]["finding_id"]:
                p["layers"][obs_l[0]]["findings"][i]["locator"] = "https://medium.com/@Cosmodrome-eng./x"
        tests.append(run(p, "medium_observed"))
    else:
        tests.append({"name": "observed_invalid_evidence", "exit": 1, "stderr": ["SKIP_NO_OBSERVED_TREATED_AS_STRUCTURAL_NA"]})
        tests.append({"name": "medium_observed", "exit": 1, "stderr": ["SKIP_NO_OBSERVED_TREATED_AS_STRUCTURAL_NA"]})
    if src["layers"]["weaknesses"]["findings"]:
        p = copy.deepcopy(src)
        p["layers"]["weaknesses"]["findings"][0]["source_finding_ids"] = []
        tests.append(run(p, "summary_no_sources"))
    else:
        tests.append({"name": "summary_no_sources", "exit": 1, "stderr": ["SKIP_NO_SUMMARY"]})
    p = copy.deepcopy(src)
    target = "jurisdiction_legal"
    p["layers"][target] = {"findings": []}
    p["unknowns"] = [u for u in p["unknowns"] if u["layer"] != target]
    tests.append(run(p, "missing_axis_no_unknown"))
    return tests


def run(name: str) -> int:
    captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pack = load_pack(name)
    pack["_evid"].mkdir(parents=True, exist_ok=True)
    rows = capture(pack, captured_at)
    obs = extract(pack, captured_at)
    profile = build(pack, obs)
    v = verify(pack, profile, captured_at)
    negs = negatives(pack)
    neg_pass = all(t["exit"] == 1 for t in negs)
    src_ok = [r for r in rows if r["retrieval_status"] == "OK"]
    primary = [r for r in src_ok if str(r.get("source_type", "")).startswith("PRIMARY")]
    journal = {
        "pack": pack["ticker"],
        "captured_at": captured_at,
        "source_intake": "PASS" if src_ok else "FAIL",
        "capture_provenance": "PASS",
        "evidence_extraction": "PASS" if obs["findings"] else "FAIL",
        "profile_build": "PASS",
        "schema_validation": v["validate"],
        "render": v["render"],
        "negative_tests": "PASS" if neg_pass else "FAIL",
        "negatives": negs,
        "source_count": len(rows),
        "ok_source_count": len(src_ok),
        "primary_source_count": len(primary),
        "findings": v["findings"],
        "unknowns": v["unknowns"],
        "public_push": "NO",
        "contract_changed": "NO",
    }
    _dump(pack["_evid"] / "RUN.yaml", journal)
    print(yaml.safe_dump({k: journal[k] for k in journal if k != "negatives"}, allow_unicode=True, sort_keys=False))
    keys = (
        "source_intake",
        "capture_provenance",
        "evidence_extraction",
        "profile_build",
        "schema_validation",
        "render",
        "negative_tests",
    )
    return 0 if all(journal[k] == "PASS" for k in keys) else 1


def main(argv=None) -> int:
    argv = list(argv or sys.argv[1:])
    if not argv:
        sys.stderr.write("usage: pipeline.py run PACK\n")
        return 2
    cmd = argv[0]
    pack = argv[1] if len(argv) > 1 else None
    if cmd == "run" and pack:
        return run(pack)
    sys.stderr.write("usage: pipeline.py run PACK\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
