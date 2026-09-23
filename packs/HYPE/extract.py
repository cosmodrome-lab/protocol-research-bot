"""HYPE pack extractor. Phrase rules over captured official bodies."""
from __future__ import annotations

import json


def extract(ctx):
    F, U, findings, unknowns = ctx.F, ctx.U, [], []

    if ctx.ok("S-ABOUT"):
        t = ctx.text("S-ABOUT")
        if "HyperCore" in t and "HyperEVM" in t:
            findings.append(F("HYPE-F-001", "smart_contracts",
                "Official docs declare L1 execution split into HyperCore and HyperEVM.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-ABOUT"],
                "Official docs retract the HyperCore/HyperEVM split.",
                "Declaration in captured markdown, not a code audit."))
        if "fully onchain perpetual futures and spot order books" in t:
            findings.append(F("HYPE-F-002", "smart_contracts",
                "Official docs declare HyperCore holds onchain perpetual and spot order books.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-ABOUT"],
                "Official docs describe off-chain books as the live model."))
        if "HyperBFT" in t:
            findings.append(F("HYPE-F-003", "architectural_dependencies",
                "Official docs declare consensus as HyperBFT.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-ABOUT"],
                "Official docs name a different consensus."))

    if ctx.ok("S-BOOK") and "price-time priority" in ctx.text("S-BOOK"):
        findings.append(F("HYPE-F-004", "market_structure",
            "Official order-book page declares CEX-like books with price-time priority.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-BOOK"],
            "Official docs describe AMM-only matching."))

    if ctx.ok("S-AUDITS"):
        t = ctx.text("S-AUDITS")
        if "legacy bridge contract has been audited by Zellic" in t:
            findings.append(F("HYPE-F-010", "audits",
                "Official audits page declares a Zellic audit of the legacy bridge contract, not of HyperCore matching/liquidation.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-AUDITS"],
                "Official audits page lists a HyperCore matching-engine audit with commit/bytecode hash.",
                "Embedded Zellic PDF bytes were not captured."))
        findings.append(F("HYPE-F-012", "audits",
            "This capture does not contain an official statement that running HyperCore execution is in any published audit scope.",
            "NOT_PROVEN", "PRIMARY_LOCATED", ["S-AUDITS"],
            "Audits page names HyperCore matching/liquidation bytecode and audit hash.",
            "Absence of a sentence is not proof that no other audit exists off this page."))

    if ctx.ok("S-STAKING"):
        t = ctx.text("S-STAKING")
        if "10k HYPE" in t:
            findings.append(F("HYPE-F-020", "tokenomics",
                "Official staking page declares a 10k HYPE self-delegation requirement for an active validator.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-STAKING"],
                "Official docs drop the 10k HYPE threshold."))
        if "more than ⅔ of the total stake" in t:
            findings.append(F("HYPE-F-021", "governance",
                "Official staking page declares a quorum as any validator set with more than two-thirds of total stake.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-STAKING"],
                "Official docs define quorum differently."))
        if "Validators may vote to jail peers" in t:
            findings.append(F("HYPE-F-022", "governance",
                "Official staking page declares validators may jail peers; jailing is not slashing.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-STAKING"],
                "Official docs retract peer-jail."))

    if ctx.ok("S-ORACLE") and "validators are responsible for publishing spot oracle prices" in ctx.text("S-ORACLE").lower():
        findings.append(F("HYPE-F-040", "validators_sequencers_nodes_oracles",
            "Official oracle page declares validators publish spot oracle prices; final oracle is stake-weighted median of submissions.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-ORACLE"],
            "Official docs describe an external-only oracle with no validator submission."))

    if ctx.ok("S-API-VAL"):
        data = json.loads(ctx.text("S-API-VAL"))
        active = [v for v in data if v.get("isActive")]
        stakes = sorted((int(v.get("stake") or 0) for v in active), reverse=True)
        total = sum(stakes) or 1
        findings.append(F("HYPE-F-041", "validators_sequencers_nodes_oracles",
            f"Official info API validatorSummaries at capture listed {len(data)} validators, {len(active)} active.",
            "OBSERVED", "PRIMARY_CAPTURED", ["S-API-VAL"],
            "A later capture of the same endpoint lists a different count at the same timestamp.",
            "Observation of the captured API body only."))
        findings.append(F("HYPE-F-042", "validators_sequencers_nodes_oracles",
            f"In the captured active set, stake shares were top1={stakes[0]/total:.4f}, top3={sum(stakes[:3])/total:.4f}.",
            "DERIVED", "PRIMARY_CAPTURED", ["S-API-VAL"],
            "Recompute from the same captured JSON yields different shares.",
            extra={"source_finding_ids": ["HYPE-F-041"]}))

    if ctx.ok("S-API-META"):
        n = len((json.loads(ctx.text("S-API-META")) or {}).get("universe") or [])
        findings.append(F("HYPE-F-090", "market_structure",
            f"Official info API meta.universe at capture listed {n} perp assets.",
            "OBSERVED", "PRIMARY_CAPTURED", ["S-API-META"],
            "Re-parse of the captured JSON yields a different universe length."))

    if ctx.ok("S-CONTRIB") and "Hyperliquid Labs is a core contributor" in ctx.text("S-CONTRIB"):
        findings.append(F("HYPE-F-060", "founders_management_entities",
            "Official contributors page declares Hyperliquid Labs as a core contributor, led by Jeff and iliensinc.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-CONTRIB"],
            "Official page retracts Labs attribution.",
            "Self-declaration. Not independent legal identity confirmation."))

    if ctx.ok("S-VAULTS") and "Hyperliquidity Provider (HLP)" in ctx.text("S-VAULTS"):
        findings.append(F("HYPE-F-080", "treasury_custody_bridges_keys",
            "Official protocol-vaults page declares HLP as a protocol vault that market-makes, liquidates, and accrues a portion of trading fees.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-VAULTS"],
            "Official page retracts HLP fee accrual.",
            "Signer set not in this capture."))

    if ctx.ok("S-FEES"):
        t = ctx.text("S-FEES").lower()
        if "assistance fund" not in t and "buyback" not in t:
            findings.append(F("HYPE-F-030", "revenue_to_token",
                "Captured official fees page does not declare an un-switchable route from protocol fees to HYPE holders.",
                "NOT_PROVEN", "PRIMARY_LOCATED", ["S-FEES"],
                "Fees page adds a mandatory holder entitlement path.",
                "Not proof that no such path exists elsewhere."))

    if ctx.ok("S-LLMS"):
        findings.append(F("HYPE-F-100", "disclosure_quality",
            "Official docs publish a machine-readable index (llms.txt) and markdown mirrors.",
            "OBSERVED", "PRIMARY_CAPTURED", ["S-LLMS"],
            "llms.txt is gone at the captured URL."))

    if any(f["finding_id"] == "HYPE-F-002" for f in findings) and any(f["finding_id"] == "HYPE-F-012" for f in findings):
        findings.append(F("HYPE-F-120", "declared_vs_observed",
            "Docs declare onchain books. This run observed those sentences and the API validator set. It did not observe HyperCore source or a matching-engine audit.",
            "DERIVED", "PRIMARY_LOCATED", ["S-ABOUT", "S-AUDITS"],
            "A captured official source publishes HyperCore matching source plus audit hash.",
            extra={"source_finding_ids": ["HYPE-F-002", "HYPE-F-012", "HYPE-F-100"]}))

    unknowns += [
        U("HYPE-U-001", "audits", "Does any published audit cover running HyperCore matching bytecode?",
          "Bridge audit is not core-execution audit.", "Audit PDF + bytecode hash."),
        U("HYPE-U-002", "revenue_to_token", "Is there an un-switchable route from protocol revenue to HYPE holders?",
          "Fee schedule ≠ holder entitlement.", "Rule/code without admin off-switch."),
        U("HYPE-U-003", "treasury_custody_bridges_keys", "HLP / treasury / bridge signer sets?",
          "HLP role is declared; keys are not.", "Address registry + threshold."),
        U("HYPE-U-004", "validators_sequencers_nodes_oracles", "Which validators are Foundation-affiliated?",
          "API gives names and stake, not control graph.", "Identity map."),
        U("HYPE-U-005", "tokenomics", "Free float / unlocks / insider inventory on as_of?",
          "Staking threshold is not circulating supply.", "Date-aligned snapshot."),
        U("HYPE-U-006", "jurisdiction_legal", "Full legal map of Labs / Foundation / HPC?",
          "Contributors page names Labs, not a registry.", "Primary filings."),
        U("HYPE-U-007", "smart_contracts", "Is HyperCore matching source public and reproducible?",
          "Docs describe behaviour; they are not the binary.", "Public tree + build hash."),
        U("HYPE-U-008", "governance", "Can HYPE holders change HyperCore parameters without the validator path?",
          "Quorum and jail are validator-set mechanics.", "Observed proposal → executed change without that path."),
    ]
    return findings, unknowns
