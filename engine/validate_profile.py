#!/usr/bin/env python3
"""Protocol Research Bot V1 — init / validate / render.

Law: product/protocol_research_bot/CONTRACT_V1.yaml
Does not read Forensic stores. Does not recommend.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required\n")
    sys.exit(2)

CONTRACT = "cosm.bot.contract/1.0.0"

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
SUMMARY = ["weaknesses", "strengths"]
EPI = {
    "OBSERVED",
    "DERIVED",
    "ESTIMATED",
    "HYPOTHESIS",
    "DECLARED_ONLY",
    "NOT_PROVEN",
}
EVID = {
    "PRIMARY_CAPTURED",
    "PRIMARY_LOCATED",
    "SECONDARY",
    "RECONSTRUCTED",
    "ABSENT",
}
COMPAT = {
    "OBSERVED": {"PRIMARY_CAPTURED", "PRIMARY_LOCATED"},
    "DERIVED": {"PRIMARY_CAPTURED", "PRIMARY_LOCATED", "SECONDARY"},
    "ESTIMATED": {"PRIMARY_CAPTURED", "PRIMARY_LOCATED", "SECONDARY"},
    "HYPOTHESIS": {"SECONDARY", "RECONSTRUCTED", "ABSENT"},
    "DECLARED_ONLY": {"PRIMARY_LOCATED", "SECONDARY"},
    "NOT_PROVEN": {"PRIMARY_LOCATED", "SECONDARY", "RECONSTRUCTED", "ABSENT"},
}
BANNED = re.compile(
    r"\b(buy|sell|accumulate|allocate|price target|undervalued|overvalued)\b",
    re.I,
)
SELF_SPEECH = re.compile(
    r"medium\.com/@cosmodrome-eng|cosmodrome-eng\.|bot-hype-|cosm\.bot",
    re.I,
)


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("file must be a mapping")
    return data


def dump(data: dict) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def short(protocol: str) -> str:
    letters = re.sub(r"[^A-Za-z0-9]", "", protocol)
    return (letters[:8] or "PROTO").upper()


def init_profile(intake: dict) -> dict:
    missing = [k for k in ("protocol", "ticker", "as_of") if not intake.get(k)]
    if missing:
        raise ValueError(f"intake missing {missing}")
    proto = str(intake["protocol"])
    ticker = str(intake["ticker"])
    token = re.sub(r"[^A-Za-z0-9]", "", ticker).upper() or short(proto)
    layers = {lid: {"findings": []} for lid in ANALYSIS}
    unknowns = []
    for lid in ANALYSIS:
        unknowns.append(
            {
                "unknown_id": f"{token}-U-{lid[:12].upper()}",
                "layer": lid,
                "question": f"Layer {lid} not yet analysed for {proto}.",
                "why_material": "Unfilled analysis layer is residual risk, not empty risk.",
                "what_would_close_it": "At least one finding with locator and falsifier, or a tighter unknown question.",
            }
        )
    return {
        "profile_id": f"BOT-{token}-000",
        "protocol": proto,
        "ticker": ticker,
        "profile_rev": "r0",
        "as_of": str(intake["as_of"]),
        "contract": CONTRACT,
        "state": "SKELETON",
        "sources": intake.get("sources") or [],
        "forbidden_outputs": ["BUY", "SELL", "HOLD", "letter_grade", "price_target"],
        "layers": layers,
        "unknowns": unknowns,
    }


def _findings(p: dict) -> list[dict]:
    out = []
    for lid, body in (p.get("layers") or {}).items():
        for f in (body or {}).get("findings") or []:
            out.append(f)
    return out


def errors(p: dict) -> list[str]:
    err: list[str] = []
    for k in (
        "profile_id",
        "protocol",
        "ticker",
        "profile_rev",
        "as_of",
        "contract",
        "layers",
        "unknowns",
        "forbidden_outputs",
    ):
        if k not in p:
            err.append(f"missing top-level field: {k}")
    if p.get("contract") != CONTRACT:
        err.append(f"contract must be {CONTRACT}")
    if not isinstance(p.get("layers"), dict):
        err.append("layers must be a mapping")
        return err
    layers = p["layers"]
    for lid in ANALYSIS:
        if lid not in layers:
            err.append(f"missing analysis layer: {lid}")
    fo = p.get("forbidden_outputs") or []
    for must in ("BUY", "SELL"):
        if must not in fo:
            err.append(f"forbidden_outputs must include {must}")

    unknowns = p.get("unknowns")
    if not isinstance(unknowns, list) or not unknowns:
        err.append("unknowns must be a non-empty list")
        unknowns = []
    pointed = set()
    for i, u in enumerate(unknowns):
        for rk in ("unknown_id", "layer", "question", "why_material", "what_would_close_it"):
            if not (u or {}).get(rk):
                err.append(f"unknowns[{i}] missing {rk}")
        if (u or {}).get("layer"):
            pointed.add(u["layer"])

    ids = []
    for lid, body in layers.items():
        if lid not in ANALYSIS + SUMMARY:
            err.append(f"unknown layer key: {lid}")
        findings = (body or {}).get("findings") or []
        if lid in ANALYSIS and not findings and lid not in pointed:
            err.append(f"layer {lid} has no findings and no unknown_slot")
        for i, f in enumerate(findings):
            pref = f"{lid}[{i}]"
            for rk in ("finding_id", "layer", "claim", "epistemology", "evidence_status", "falsifier"):
                if not f.get(rk):
                    err.append(f"{pref} missing {rk}")
            if f.get("layer") and f["layer"] != lid:
                err.append(f"{pref} layer field != parent key")
            epi = f.get("epistemology")
            ev = f.get("evidence_status")
            if epi == "UNKNOWN":
                err.append(f"{pref} UNKNOWN is not a finding epistemology — use unknowns[]")
            if epi and epi not in EPI:
                err.append(f"{pref} bad epistemology {epi}")
            if ev and ev not in EVID:
                err.append(f"{pref} bad evidence_status {ev}")
            if epi in COMPAT and ev and ev not in COMPAT[epi]:
                err.append(f"{pref} incompatible {epi} + {ev}")
            if ev == "PRIMARY_CAPTURED" and not f.get("artifact_hash"):
                err.append(f"{pref} PRIMARY_CAPTURED requires artifact_hash")
            loc = (f.get("locator") or "").strip()
            if ev != "ABSENT" and not loc:
                err.append(f"{pref} locator required unless ABSENT")
            if BANNED.search(f.get("claim") or ""):
                err.append(f"{pref} banned recommendation language")
            if epi == "OBSERVED" and loc and SELF_SPEECH.search(loc):
                err.append(f"{pref} OBSERVED cannot rest on COSMODROME self-speech")
            if ev in ("PRIMARY_CAPTURED", "PRIMARY_LOCATED") and loc and SELF_SPEECH.search(loc):
                err.append(f"{pref} self-speech cannot be primary evidence")
            if lid == "weaknesses" and epi and epi != "DERIVED":
                err.append(f"{pref} weaknesses must be DERIVED")
            if lid == "strengths" and epi and epi not in ("OBSERVED", "DERIVED"):
                err.append(f"{pref} strengths must be OBSERVED or DERIVED")
            if lid in SUMMARY and not f.get("source_finding_ids"):
                err.append(f"{pref} summary finding needs source_finding_ids")
            if f.get("finding_id"):
                ids.append(f["finding_id"])
            if epi == "DERIVED" and ev == "SECONDARY" and not f.get("source_finding_ids"):
                err.append(f"{pref} DERIVED+SECONDARY needs source_finding_ids")

    if len(ids) != len(set(ids)):
        err.append("duplicate finding_id")
    idset = set(ids)
    for lid in SUMMARY:
        for f in (layers.get(lid) or {}).get("findings") or []:
            for sid in f.get("source_finding_ids") or []:
                if sid not in idset:
                    err.append(f"{lid} source_finding_id not in profile: {sid}")

    if p.get("fif_dimensions_questions_only", {}).get("letter_grade") not in (None, "FORBIDDEN_IN_V1"):
        err.append("V1 must not publish letter_grade")
    return err


def render(p: dict) -> str:
    lines = [
        f"# PROTOCOL FORENSIC PROFILE — {p.get('protocol')} ({p.get('ticker')})",
        "",
        f"profile_id: {p.get('profile_id')}  rev: {p.get('profile_rev')}  as_of: {p.get('as_of')}",
        f"contract: {p.get('contract')}",
        "",
        "THIS IS NOT A BUY OR SELL RECOMMENDATION.",
        "THIS IS NOT A CREDIT RATING AND NOT A COURT-READY FORENSIC REVISION.",
        "UNKNOWN / NOT_PROVEN are valid results. Missing data is not missing risk.",
        "",
    ]
    for lid in ANALYSIS:
        body = (p.get("layers") or {}).get(lid) or {}
        lines.append(f"## {lid}")
        lines.append("")
        findings = body.get("findings") or []
        if not findings:
            lines.append("- (no findings — see unknowns)")
            lines.append("")
        for f in findings:
            lines.append(
                f"- `{f.get('finding_id')}` [{f.get('epistemology')} / {f.get('evidence_status')}]"
            )
            lines.append(f"  {f.get('claim')}")
            lines.append(f"  locator: {f.get('locator') or '—'}")
            lines.append(f"  falsifier: {f.get('falsifier')}")
            lines.append("")
    for lid in SUMMARY:
        body = (p.get("layers") or {}).get(lid)
        if not body:
            continue
        lines.append(f"## {lid}")
        lines.append("")
        for f in body.get("findings") or []:
            lines.append(
                f"- `{f.get('finding_id')}` [{f.get('epistemology')} / {f.get('evidence_status')}]"
            )
            lines.append(f"  {f.get('claim')}")
            lines.append(f"  from: {', '.join(f.get('source_finding_ids') or [])}")
            lines.append("")
    lines.append("## unknowns")
    lines.append("")
    for u in p.get("unknowns") or []:
        lines.append(f"- `{u.get('unknown_id')}` ({u.get('layer')})")
        lines.append(f"  Q: {u.get('question')}")
        lines.append(f"  why material: {u.get('why_material')}")
        lines.append(f"  closes if: {u.get('what_would_close_it')}")
        lines.append("")
    lines.append("## stop")
    lines.append("")
    lines.append("Investor decision sits outside this file.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="protocol-research-bot")
    ap.add_argument("command", choices=["init", "validate", "render"])
    ap.add_argument("path")
    ap.add_argument("-o", "--output", help="write init/render to this path")
    args = ap.parse_args(argv)
    path = Path(args.path)
    try:
        data = load(path)
    except Exception as e:
        sys.stderr.write(f"load error: {e}\n")
        return 2

    if args.command == "init":
        try:
            profile = init_profile(data)
        except ValueError as e:
            sys.stderr.write(f"intake error: {e}\n")
            return 2
        text = dump(profile)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        print("SKELETON", profile["profile_id"], file=sys.stderr)
        return 0

    err = errors(data)
    if err:
        sys.stderr.write("INVALID\n")
        for e in err:
            sys.stderr.write(f"- {e}\n")
        return 1
    if args.command == "validate":
        nfind = len(_findings(data))
        print(
            f"VALID {data['profile_id']} {data['profile_rev']} "
            f"findings={nfind} unknowns={len(data['unknowns'])}"
        )
        return 0
    text = render(data)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
