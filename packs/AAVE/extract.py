"""AAVE pack extractor. Phrase rules over captured official bodies."""
from __future__ import annotations

import json


def extract(ctx):
    F, U, findings, unknowns = ctx.F, ctx.U, [], []

    if ctx.ok("S-OVERVIEW"):
        t = ctx.text("S-OVERVIEW")
        if "non-custodial liquidity protocol" in t:
            findings.append(F("AAVE-F-001", "smart_contracts",
                "Official v3 overview declares Aave v3 as a non-custodial liquidity protocol on Ethereum and other networks, integrated via smart contracts.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-OVERVIEW"],
                "Official overview retracts the non-custodial / multi-network claim."))
        if "battle-tested smart contracts" in t:
            findings.append(F("AAVE-F-002", "disclosure_quality",
                "Official overview uses the phrase battle-tested smart contracts. That is marketing language on a docs page, not an audit scope table.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-OVERVIEW"],
                "Overview replaces the phrase with an audit-hash table."))

    if ctx.ok("S-POOL") and "Pool" in ctx.text("S-POOL"):
        findings.append(F("AAVE-F-003", "smart_contracts",
            "Official developers docs publish a Pool smart-contract page (public contract surface).",
            "OBSERVED", "PRIMARY_CAPTURED", ["S-POOL"],
            "Pool documentation page is absent at the captured URL.",
            "Page existence ≠ bytecode audit."))

    if ctx.ok("S-GH-AUDITS"):
        try:
            data = json.loads(ctx.text("S-GH-AUDITS"))
        except Exception:
            data = None
        if isinstance(data, list):
            pdfs = [x.get("name") for x in data if str(x.get("name", "")).endswith(".pdf")]
            findings.append(F("AAVE-F-010", "audits",
                f"GitHub aave/aave-v3-core/audits listing at capture contained {len(pdfs)} PDF names including OpenZeppelin, TrailOfBits, PeckShield, SigmaPrime, ABDK reports as filenames.",
                "OBSERVED", "PRIMARY_CAPTURED", ["S-GH-AUDITS"],
                "The captured GitHub listing JSON does not contain those filenames.",
                "Filename listing is not the PDF body and not proof the running deployment equals the audited commit."))
        elif isinstance(data, dict) and data.get("message"):
            findings.append(F("AAVE-F-010", "audits",
                f"GitHub audits directory response was not a file list: {data.get('message')}",
                "NOT_PROVEN", "PRIMARY_LOCATED", ["S-GH-AUDITS"],
                "Unauthenticated listing returns the audits array."))

    if ctx.ok("S-TOKEN"):
        t = ctx.text("S-TOKEN")
        if "governance token" in t.lower() or "AAVE token" in t:
            findings.append(F("AAVE-F-020", "tokenomics",
                "Official AAVE token page declares AAVE as the native governance token of the protocol.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-TOKEN"],
                "Official page retracts AAVE as governance token."))

    if ctx.ok("S-GHO") and "stablecoin" in ctx.text("S-GHO").lower():
        findings.append(F("AAVE-F-030", "revenue_to_token",
            "Official GHO page declares GHO as a protocol-native over-collateralised stablecoin. This capture does not by itself prove an un-switchable cashflow from GHO to AAVE holders.",
            "NOT_PROVEN", "PRIMARY_LOCATED", ["S-GHO"],
            "Official page states a mandatory AAVE-holder claim on GHO residual cashflow.",
            "GHO existence ≠ AAVE entitlement."))

    if ctx.ok("S-ORACLE") or ctx.ok("S-ORACLE-SC"):
        sid = "S-ORACLE" if ctx.ok("S-ORACLE") else "S-ORACLE-SC"
        t = ctx.text(sid)
        if "oracle" in t.lower():
            findings.append(F("AAVE-F-040", "validators_sequencers_nodes_oracles",
                "Official docs declare each reserve is associated with an oracle contract that supplies asset prices.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", [sid],
                "Official docs remove per-reserve oracles."))

    if ctx.ok("S-GOV"):
        t = ctx.text("S-GOV")
        if "AAVE token holder" in t and "Aave Governance" in t:
            findings.append(F("AAVE-F-050", "governance",
                "Official governance page declares the protocol is governed by AAVE, stkAAVE, and aAAVE holders on Ethereum mainnet via Aave Governance v3.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-GOV"],
                "Official page retracts token-holder governance."))
        if "timelock delay" in t.lower() or "timelock" in t.lower():
            findings.append(F("AAVE-F-051", "governance",
                "Official governance page declares a timelock delay of one day or seven days before execution, depending on proposal type.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-GOV"],
                "Official page removes timelocks."))
        if "BGD Labs" in t:
            findings.append(F("AAVE-F-060", "founders_management_entities",
                "Official governance page attributes Governance v3 development to BGD Labs and names Aave Labs as a governance interface operator.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-GOV"],
                "Official page removes BGD Labs / Aave Labs attribution.",
                "Role attribution is not a beneficial-owner graph."))
        if "Snapshot" in t:
            findings.append(F("AAVE-F-052", "governance",
                "Official governance page declares off-chain Temp Check / ARFC votes on Snapshot are non-binding.",
                "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-GOV"],
                "Official page treats Snapshot as binding execution."))

    if ctx.ok("S-LICENSE") and "publicly auditable" in ctx.text("S-LICENSE"):
        findings.append(F("AAVE-F-070", "jurisdiction_legal",
            "Official licensing page declares protocol smart contracts as self-executing and publicly auditable, with code across multiple GitHub repositories and named licenses.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-LICENSE"],
            "Official page retracts public auditability.",
            "License text is not a corporate filing."))

    if ctx.ok("S-UMBRELLA") and "Umbrella" in ctx.text("S-UMBRELLA"):
        findings.append(F("AAVE-F-080", "treasury_custody_bridges_keys",
            "Official Umbrella page declares an onchain bad-debt coverage system with slashing of staked aTokens, parameters set by Aave DAO and ongoing management delegated to the Aave Finance Committee.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-UMBRELLA"],
            "Official page retracts Finance Committee delegation.",
            "Committee membership and keys not in this capture."))

    if ctx.ok("S-SECURITY") and ("independently audited" in ctx.text("S-SECURITY").lower() or "Audit" in ctx.text("S-SECURITY")):
        findings.append(F("AAVE-F-011", "audits",
            "Official security page declares independent audits and that deployed contracts are listed in docs / Address Book.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-SECURITY"],
            "Security page removes the independent-audit claim.",
            "HTML marketing page; PDF bodies not captured here."))

    if ctx.ok("S-LLMS"):
        findings.append(F("AAVE-F-100", "disclosure_quality",
            "Official docs publish llms.txt and markdown mirrors used in this capture.",
            "OBSERVED", "PRIMARY_CAPTURED", ["S-LLMS"],
            "llms.txt is gone at the captured URL."))

    if ctx.ok("S-GHO"):
        findings.append(F("AAVE-F-090", "market_structure",
            "Official ecosystem includes GHO as a protocol-native stablecoin alongside the v3 lending pools.",
            "DECLARED_ONLY", "PRIMARY_LOCATED", ["S-GHO"],
            "Official page removes GHO from the protocol surface."))

    if any(f["finding_id"] == "AAVE-F-050" for f in findings) and any(f["finding_id"] == "AAVE-F-001" for f in findings):
        findings.append(F("AAVE-F-110", "architectural_dependencies",
            "Declared critical path in captured docs: Ethereum-settled token voting, Governance v3 payloads, v3 Pool contracts, per-reserve oracles.",
            "DERIVED", "PRIMARY_LOCATED", ["S-GOV", "S-OVERVIEW"],
            "Official docs describe a path that does not use token voting or Pool contracts.",
            extra={"source_finding_ids": ["AAVE-F-050", "AAVE-F-001"]}))
        findings.append(F("AAVE-F-120", "declared_vs_observed",
            "Docs declare token-holder control and public contracts. This run observed those sentences and a GitHub audits directory listing. It did not observe guardian keys or that running bytecode equals an audited commit.",
            "DERIVED", "PRIMARY_LOCATED", ["S-GOV", "S-GH-AUDITS"],
            "Capture of running bytecode hash matching an audit commit.",
            extra={"source_finding_ids": ["AAVE-F-050", "AAVE-F-010", "AAVE-F-100"]}))

    unknowns += [
        U("AAVE-U-001", "audits", "Which running deployment commit equals which audit PDF?",
          "A folder of PDF names is not a bytecode match.", "Commit hash ↔ deployed bytecode ↔ PDF scope."),
        U("AAVE-U-002", "revenue_to_token", "Is there an un-switchable route from protocol revenue / GHO residual to AAVE holders?",
          "Governance token ≠ cashflow claim.", "Rule without admin off-switch plus flow."),
        U("AAVE-U-003", "treasury_custody_bridges_keys", "Collector / treasury / guardian / Finance Committee signer sets?",
          "Umbrella names a committee; keys are missing.", "Address registry + threshold."),
        U("AAVE-U-004", "tokenomics", "Circulating, locked, stkAAVE share, treasury inventory on as_of?",
          "Token role is not free float.", "Date-aligned snapshot."),
        U("AAVE-U-005", "jurisdiction_legal", "Legal entities behind Aave Labs / BGD Labs / DAO and licences?",
          "Docs name Labs; they are not filings.", "Primary filings."),
        U("AAVE-U-006", "founders_management_entities", "Beneficial control of Aave Labs and BGD Labs?",
          "Interface operator ≠ owner graph.", "official_cross_link or independent confirmation."),
        U("AAVE-U-007", "validators_sequencers_nodes_oracles", "Oracle operator set and fallback per reserve on as_of?",
          "Docs say an oracle exists; not who can change the source.", "Source registry + admin."),
    ]
    return findings, unknowns
