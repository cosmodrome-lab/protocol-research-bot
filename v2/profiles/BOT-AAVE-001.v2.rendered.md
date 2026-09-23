# PROTOCOL FORENSIC PROFILE — Aave (AAVE)

profile_id: BOT-AAVE-001  rev: r1-v2  as_of: 2026-09-23
contract: cosm.bot.contract/1.0.0

THIS IS NOT A BUY OR SELL RECOMMENDATION.
THIS IS NOT A CREDIT RATING AND NOT A COURT-READY FORENSIC REVISION.
UNKNOWN / NOT_PROVEN are valid results. Missing data is not missing risk.

## smart_contracts

- `AAVE-F-001` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official v3 overview declares Aave v3 as a non-custodial liquidity protocol on Ethereum and other networks, integrated via smart contracts.
  locator: https://aave.com/docs/aave-v3/overview.md
  falsifier: Official overview retracts the non-custodial / multi-network claim.

- `AAVE-F-003` [OBSERVED / PRIMARY_CAPTURED]
  Official developers docs publish a Pool smart-contract page (public contract surface).
  locator: https://aave.com/docs/developers/smart-contracts/pool.md
  falsifier: Pool documentation page is absent at the captured URL.

- `AAVE-F-V2-002` [OBSERVED / PRIMARY_CAPTURED]
  Official bgd-labs address book names Ethereum V3 POOL proxy 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2 and POOL_IMPL 0x97287a4F35E583D924f78AD88DB8AFcE1379189A. Runtime bytecode of POOL_IMPL captured 2026-09-23 hashes to 9d8a157668b6964beac5531dcb7150dc639dc184dc2e1962cb9036801c71cf34.
  locator: https://raw.githubusercontent.com/bgd-labs/aave-address-book/main/src/AaveV3Ethereum.sol
  falsifier: Re-fetch of address book or eth_getCode at same as_of disagrees.

## audits

- `AAVE-F-010` [OBSERVED / PRIMARY_CAPTURED]
  GitHub aave/aave-v3-core/audits listing at capture contained 8 PDF names including OpenZeppelin, TrailOfBits, PeckShield, SigmaPrime, ABDK reports as filenames.
  locator: https://api.github.com/repos/aave/aave-v3-core/contents/audits
  falsifier: The captured GitHub listing JSON does not contain those filenames.

- `AAVE-F-011` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official security page declares independent audits and that deployed contracts are listed in docs / Address Book.
  locator: https://aave.com/security
  falsifier: Security page removes the independent-audit claim.

- `AAVE-F-V2-003` [NOT_PROVEN / PRIMARY_LOCATED]
  Historical OpenZeppelin Aave V3 audit (01-11-2021 filename in official aave-v3-core/audits listing) states scope commit 14f6148e21b477d78347db6a1603039c9559e275. No captured primary source states that 2026-09-23 POOL_IMPL bytecode equals that commit.
  locator: https://github.com/aave/aave-v3-core/blob/master/audits/01-11-2021_OpenZeppelin_AaveV3.pdf
  falsifier: Primary source binds current POOL_IMPL bytecode hash to that audit commit.

## tokenomics

- `AAVE-F-020` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official AAVE token page declares AAVE as the native governance token of the protocol.
  locator: https://aave.com/docs/ecosystem/aave.md
  falsifier: Official page retracts AAVE as governance token.

## revenue_to_token

- `AAVE-F-030` [NOT_PROVEN / PRIMARY_LOCATED]
  Official GHO page declares GHO as a protocol-native over-collateralised stablecoin. This capture does not by itself prove an un-switchable cashflow from GHO to AAVE holders.
  locator: https://aave.com/docs/ecosystem/gho.md
  falsifier: Official page states a mandatory AAVE-holder claim on GHO residual cashflow.

## validators_sequencers_nodes_oracles

- `AAVE-F-040` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official docs declare each reserve is associated with an oracle contract that supplies asset prices.
  locator: https://aave.com/docs/ecosystem/oracle.md
  falsifier: Official docs remove per-reserve oracles.

## governance

- `AAVE-F-050` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official governance page declares the protocol is governed by AAVE, stkAAVE, and aAAVE holders on Ethereum mainnet via Aave Governance v3.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Official page retracts token-holder governance.

- `AAVE-F-051` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official governance page declares a timelock delay of one day or seven days before execution, depending on proposal type.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Official page removes timelocks.

- `AAVE-F-052` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official governance page declares off-chain Temp Check / ARFC votes on Snapshot are non-binding.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Official page treats Snapshot as binding execution.

- `AAVE-F-V2-001` [DECLARED_ONLY / PRIMARY_LOCATED]
  On 2026-08-12 AaveLabs published an official ARFC to rotate Aave Governance Emergency Guardian signers, retaining 5-of-9 threshold and Safe addresses.
  locator: https://governance.aave.com/t/arfc-aave-governance-emergency-guardian-signer-rotation/25469
  falsifier: Primary forum JSON is not authored by AaveLabs or does not describe guardian signer rotation.

## founders_management_entities

- `AAVE-F-060` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official governance page attributes Governance v3 development to BGD Labs and names Aave Labs as a governance interface operator.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Official page removes BGD Labs / Aave Labs attribution.

## jurisdiction_legal

- `AAVE-F-070` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official licensing page declares protocol smart contracts as self-executing and publicly auditable, with code across multiple GitHub repositories and named licenses.
  locator: https://aave.com/docs/resources/code-licensing.md
  falsifier: Official page retracts public auditability.

## treasury_custody_bridges_keys

- `AAVE-F-080` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official Umbrella page declares an onchain bad-debt coverage system with slashing of staked aTokens, parameters set by Aave DAO and ongoing management delegated to the Aave Finance Committee.
  locator: https://aave.com/docs/aave-v3/umbrella.md
  falsifier: Official page retracts Finance Committee delegation.

## market_structure

- `AAVE-F-090` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official ecosystem includes GHO as a protocol-native stablecoin alongside the v3 lending pools.
  locator: https://aave.com/docs/ecosystem/gho.md
  falsifier: Official page removes GHO from the protocol surface.

## disclosure_quality

- `AAVE-F-002` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official overview uses the phrase battle-tested smart contracts. That is marketing language on a docs page, not an audit scope table.
  locator: https://aave.com/docs/aave-v3/overview.md
  falsifier: Overview replaces the phrase with an audit-hash table.

- `AAVE-F-100` [OBSERVED / PRIMARY_CAPTURED]
  Official docs publish llms.txt and markdown mirrors used in this capture.
  locator: https://aave.com/docs/llms.txt
  falsifier: llms.txt is gone at the captured URL.

## architectural_dependencies

- `AAVE-F-110` [DERIVED / PRIMARY_LOCATED]
  Declared critical path in captured docs: Ethereum-settled token voting, Governance v3 payloads, v3 Pool contracts, per-reserve oracles.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Official docs describe a path that does not use token voting or Pool contracts.

## declared_vs_observed

- `AAVE-F-120` [DERIVED / PRIMARY_LOCATED]
  Docs declare token-holder control and public contracts. This run observed those sentences and a GitHub audits directory listing. It did not observe guardian keys or that running bytecode equals an audited commit.
  locator: https://aave.com/docs/ecosystem/governance.md
  falsifier: Capture of running bytecode hash matching an audit commit.

## weaknesses

- `AAVE-F-130` [DERIVED / PRIMARY_LOCATED]
  Official docs declare token-holder governance and upgradeable core contracts. This run did not capture guardian-key holders or a date-aligned treasury snapshot.
  from: AAVE-F-050, AAVE-F-001

## strengths

- `AAVE-F-140` [DERIVED / PRIMARY_CAPTURED]
  Official docs index, markdown mirrors, public GitHub audit directory reference, and on-chain voting architecture are published and were retrieved.
  from: AAVE-F-100, AAVE-F-010, AAVE-F-050

## unknowns

- `AAVE-U-001` (audits)
  Q: Which running deployment commit equals which audit PDF?
  why material: A folder of PDF names is not a bytecode match.
  closes if: Commit hash ↔ deployed bytecode ↔ PDF scope.

- `AAVE-U-002` (revenue_to_token)
  Q: Is there an un-switchable route from protocol revenue / GHO residual to AAVE holders?
  why material: Governance token ≠ cashflow claim.
  closes if: Rule without admin off-switch plus flow.

- `AAVE-U-003` (treasury_custody_bridges_keys)
  Q: Collector / treasury / guardian / Finance Committee signer sets?
  why material: Umbrella names a committee; keys are missing.
  closes if: Address registry + threshold.

- `AAVE-U-004` (tokenomics)
  Q: Circulating, locked, stkAAVE share, treasury inventory on as_of?
  why material: Token role is not free float.
  closes if: Date-aligned snapshot.

- `AAVE-U-005` (jurisdiction_legal)
  Q: Legal entities behind Aave Labs / BGD Labs / DAO and licences?
  why material: Docs name Labs; they are not filings.
  closes if: Primary filings.

- `AAVE-U-006` (founders_management_entities)
  Q: Beneficial control of Aave Labs and BGD Labs?
  why material: Interface operator ≠ owner graph.
  closes if: official_cross_link or independent confirmation.

- `AAVE-U-007` (validators_sequencers_nodes_oracles)
  Q: Oracle operator set and fallback per reserve on as_of?
  why material: Docs say an oracle exists; not who can change the source.
  closes if: Source registry + admin.

## stop

Investor decision sits outside this file.
