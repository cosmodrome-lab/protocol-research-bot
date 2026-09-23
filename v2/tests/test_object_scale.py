#!/usr/bin/env python3
"""Identity gate scale: 25 objects, not HYPE/AAVE sized."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "engine"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "v2" / "engine"))
from validate_v2 import v2_errors  # noqa: E402

CLASSES = [
    "PROTOCOL",
    "LABS",
    "DAO",
    "DEPLOYED_CONTRACT",
    "VAULT",
    "BRIDGE",
    "LISTED_MARKET",
]


def build(n: int = 25):
    objects = []
    findings = []
    for i in range(1, n + 1):
        oid = f"OBJ-SCALE-{i:02d}"
        cls = CLASSES[(i - 1) % len(CLASSES)]
        objects.append(
            {
                "object_id": oid,
                "object_class": cls,
                "canonical_name": f"Scale object {i}",
                "protocol_relation": "synthetic_non_public",
                "primary_locator": f"https://example.invalid/scale/{i}",
                "as_of": "2026-09-23",
            }
        )
        findings.append(
            {
                "finding_id": f"SCALE-F-{i:02d}",
                "layer": "smart_contracts",
                "object_id": oid,
                "claim": f"Synthetic object {i} exists for scale test only.",
                "epistemology": "NOT_PROVEN",
                "evidence_status": "ABSENT",
                "locator": f"https://example.invalid/scale/{i}",
                "falsifier": "Not a production claim.",
            }
        )
    layers = {
        "smart_contracts": {"findings": findings},
        "audits": {"findings": []},
        "tokenomics": {"findings": []},
        "revenue_to_token": {"findings": []},
        "validators_sequencers_nodes_oracles": {"findings": []},
        "governance": {"findings": []},
        "founders_management_entities": {"findings": []},
        "jurisdiction_legal": {"findings": []},
        "treasury_custody_bridges_keys": {"findings": []},
        "market_structure": {"findings": []},
        "disclosure_quality": {"findings": []},
        "architectural_dependencies": {"findings": []},
        "declared_vs_observed": {"findings": []},
        "weaknesses": {"findings": []},
        "strengths": {"findings": []},
    }
    unknowns = [
        {
            "unknown_id": f"SCALE-U-{layer}",
            "layer": layer,
            "question": "synthetic empty layer",
            "why_material": "scale test coverage",
            "what_would_close_it": "not production",
        }
        for layer in layers
        if layer not in ("smart_contracts", "weaknesses", "strengths")
    ]
    profile = {
        "profile_id": "BOT-SCALE-001",
        "protocol": "SCALE",
        "ticker": "SCALE",
        "profile_rev": "r1-v2",
        "as_of": "2026-09-23",
        "contract": "cosm.bot.contract/1.0.0",
        "v2": True,
        "v2_laws_applied": ["IDENTITY_GATE"],
        "layers": layers,
        "unknowns": unknowns,
        "forbidden_outputs": ["BUY", "SELL", "recommendation", "letter_grade"],
    }
    return profile, {"objects": objects}


if __name__ == "__main__":
    profile, registry = build(25)
    err = v2_errors(profile, registry)
    if err:
        print("OBJECT_SCALE_TEST=FAIL")
        for e in err[:20]:
            print("-", e)
        sys.exit(1)
    print("OBJECT_SCALE_TEST=PASS objects=25")
    sys.exit(0)
