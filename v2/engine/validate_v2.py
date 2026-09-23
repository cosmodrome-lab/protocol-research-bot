#!/usr/bin/env python3
"""V2 overlay validator. Does not modify CONTRACT_V1."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ENGINE = Path(__file__).resolve().parents[2] / "engine"
sys.path.insert(0, str(ENGINE))
from validate_profile import errors as v1_errors  # noqa: E402

OBJECT_CLASS = {
    "PROTOCOL",
    "LABS",
    "DAO",
    "DEPLOYED_CONTRACT",
    "VAULT",
    "BRIDGE",
    "LISTED_MARKET",
}


def load(path: Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("mapping required")
    return data


def v2_enabled(profile: dict) -> bool:
    return bool(profile.get("v2") or profile.get("v2_laws_applied"))


def collect_findings(profile: dict) -> list[dict]:
    out = []
    for layer, body in (profile.get("layers") or {}).items():
        for f in (body or {}).get("findings") or []:
            out.append(f)
    return out


def v2_errors(profile: dict, registry: dict | None = None) -> list[str]:
    err = []
    err.extend(v1_errors(profile))
    if not v2_enabled(profile):
        return err  # V2 laws not applied; V1 errors only

    allowed_ids = set()
    class_by_id = {}
    if registry:
        for obj in registry.get("objects") or []:
            oid = obj.get("object_id")
            allowed_ids.add(oid)
            class_by_id[oid] = obj.get("object_class")
            if obj.get("object_class") not in OBJECT_CLASS:
                err.append(f"object {oid} invalid object_class")
            for req in ("object_id", "object_class", "canonical_name", "primary_locator", "as_of"):
                if not obj.get(req):
                    err.append(f"object {oid} missing {req}")

    for f in collect_findings(profile):
        fid = f.get("finding_id")
        if not f.get("object_id"):
            err.append(f"{fid} missing object_id")
        elif allowed_ids and f["object_id"] not in allowed_ids:
            err.append(f"{fid} object_id not in registry")
        # Labs statement attached to protocol deployment without linkage
        oid = f.get("object_id")
        claim = (f.get("claim") or "").lower()
        if class_by_id.get(oid) == "LABS" and any(w in claim for w in ("deployed bytecode", "pool_impl", "bridge2 0x")):
            if not f.get("related_object") and not f.get("source_finding_ids"):
                err.append(f"{fid} Labs statement attached to protocol deployment without linkage")

    for rec in profile.get("bytecode_audit") or []:
        if rec.get("result") == "PROVEN":
            if not rec.get("runtime_bytecode_sha256") or rec.get("explicit_linkage") != "YES":
                err.append(f"bytecode_audit {rec.get('object_id')} cannot be PROVEN without explicit linkage")
        if rec.get("result") == "PROVEN" and not rec.get("audit_scope_id"):
            err.append(f"bytecode_audit {rec.get('object_id')} PROVEN missing audit_scope_id")

    for ev in profile.get("incidents") or []:
        eid = ev.get("event_id") or "incident"
        if not ev.get("event_id"):
            err.append(f"{eid} missing event_id")
        if not ev.get("who_could_do_it"):
            err.append(f"{eid} missing who_could_do_it")
        if not ev.get("object_id"):
            err.append(f"{eid} missing object_id")
        if not ev.get("as_of"):
            err.append(f"{eid} missing as_of")
    return err


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        sys.stderr.write("usage: validate_v2.py PROFILE [REGISTRY]\n")
        return 2
    profile = load(Path(argv[0]))
    registry = load(Path(argv[1])) if len(argv) > 1 else None
    if not v2_enabled(profile):
        print("V2_LAWS NOT_APPLIED")
        err = v1_errors(profile)
        if err:
            print("INVALID_V1")
            for e in err:
                print("-", e)
            return 1
        print("VALID_V1")
        return 0
    err = v2_errors(profile, registry)
    if err:
        print("INVALID_V2")
        for e in err:
            print("-", e)
        return 1
    print("VALID_V2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
