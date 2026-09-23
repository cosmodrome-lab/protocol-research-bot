# PROTOCOL FORENSIC PROFILE — Hyperliquid (HYPE)

profile_id: BOT-HYPE-001  rev: r3  as_of: 2026-09-23
contract: cosm.bot.contract/1.0.0

THIS IS NOT A BUY OR SELL RECOMMENDATION.
THIS IS NOT A CREDIT RATING AND NOT A COURT-READY FORENSIC REVISION.
UNKNOWN / NOT_PROVEN are valid results. Missing data is not missing risk.

## smart_contracts

- `HYPE-F-001` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official docs declare L1 execution split into HyperCore and HyperEVM.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/about-hyperliquid.md
  falsifier: Official docs retract the HyperCore/HyperEVM split.

- `HYPE-F-002` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official docs declare HyperCore holds onchain perpetual and spot order books.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/about-hyperliquid.md
  falsifier: Official docs describe off-chain books as the live model.

## audits

- `HYPE-F-010` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official audits page declares a Zellic audit of the legacy bridge contract, not of HyperCore matching/liquidation.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/audits.md
  falsifier: Official audits page lists a HyperCore matching-engine audit with commit/bytecode hash.

- `HYPE-F-012` [NOT_PROVEN / PRIMARY_LOCATED]
  This capture does not contain an official statement that running HyperCore execution is in any published audit scope.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/audits.md
  falsifier: Audits page names HyperCore matching/liquidation bytecode and audit hash.

## tokenomics

- `HYPE-F-020` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official staking page declares a 10k HYPE self-delegation requirement for an active validator.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking.md
  falsifier: Official docs drop the 10k HYPE threshold.

## revenue_to_token

- (no findings — see unknowns)

## validators_sequencers_nodes_oracles

- `HYPE-F-040` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official oracle page declares validators publish spot oracle prices; final oracle is stake-weighted median of submissions.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle.md
  falsifier: Official docs describe an external-only oracle with no validator submission.

- `HYPE-F-041` [OBSERVED / PRIMARY_CAPTURED]
  Official info API validatorSummaries at capture listed 35 validators, 27 active.
  locator: https://api.hyperliquid.xyz/info
  falsifier: A later capture of the same endpoint lists a different count at the same timestamp.

- `HYPE-F-042` [DERIVED / PRIMARY_CAPTURED]
  In the captured active set, stake shares were top1=0.1257, top3=0.3668.
  locator: https://api.hyperliquid.xyz/info
  falsifier: Recompute from the same captured JSON yields different shares.

## governance

- `HYPE-F-021` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official staking page declares a quorum as any validator set with more than two-thirds of total stake.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking.md
  falsifier: Official docs define quorum differently.

- `HYPE-F-022` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official staking page declares validators may jail peers; jailing is not slashing.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking.md
  falsifier: Official docs retract peer-jail.

## founders_management_entities

- `HYPE-F-060` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official contributors page declares Hyperliquid Labs as a core contributor, led by Jeff and iliensinc.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/about-hyperliquid/core-contributors.md
  falsifier: Official page retracts Labs attribution.

## jurisdiction_legal

- (no findings — see unknowns)

## treasury_custody_bridges_keys

- `HYPE-F-080` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official protocol-vaults page declares HLP as a protocol vault that market-makes, liquidates, and accrues a portion of trading fees.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults.md
  falsifier: Official page retracts HLP fee accrual.

## market_structure

- `HYPE-F-004` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official order-book page declares CEX-like books with price-time priority.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book.md
  falsifier: Official docs describe AMM-only matching.

- `HYPE-F-090` [OBSERVED / PRIMARY_CAPTURED]
  Official info API meta.universe at capture listed 234 perp assets.
  locator: https://api.hyperliquid.xyz/info
  falsifier: Re-parse of the captured JSON yields a different universe length.

## disclosure_quality

- `HYPE-F-100` [OBSERVED / PRIMARY_CAPTURED]
  Official docs publish a machine-readable index (llms.txt) and markdown mirrors.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt
  falsifier: llms.txt is gone at the captured URL.

## architectural_dependencies

- `HYPE-F-003` [DECLARED_ONLY / PRIMARY_LOCATED]
  Official docs declare consensus as HyperBFT.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/about-hyperliquid.md
  falsifier: Official docs name a different consensus.

## declared_vs_observed

- `HYPE-F-120` [DERIVED / PRIMARY_LOCATED]
  Docs declare onchain books. This run observed those sentences and the API validator set. It did not observe HyperCore source or a matching-engine audit.
  locator: https://hyperliquid.gitbook.io/hyperliquid-docs/about-hyperliquid.md
  falsifier: A captured official source publishes HyperCore matching source plus audit hash.

## weaknesses

- `HYPE-F-130` [DERIVED / PRIMARY_LOCATED]
  Captured official surface documents a Zellic legacy-bridge audit and does not document HyperCore matching audit or a holder revenue entitlement.
  from: HYPE-F-012, HYPE-F-010

## strengths

- `HYPE-F-140` [DERIVED / PRIMARY_CAPTURED]
  Official docs index, markdown mirrors, and a live validatorSummaries API existed at capture and were hashed as retrieved bodies.
  from: HYPE-F-100, HYPE-F-041, HYPE-F-001

## unknowns

- `HYPE-U-001` (audits)
  Q: Does any published audit cover running HyperCore matching bytecode?
  why material: Bridge audit is not core-execution audit.
  closes if: Audit PDF + bytecode hash.

- `HYPE-U-002` (revenue_to_token)
  Q: Is there an un-switchable route from protocol revenue to HYPE holders?
  why material: Fee schedule ≠ holder entitlement.
  closes if: Rule/code without admin off-switch.

- `HYPE-U-003` (treasury_custody_bridges_keys)
  Q: HLP / treasury / bridge signer sets?
  why material: HLP role is declared; keys are not.
  closes if: Address registry + threshold.

- `HYPE-U-004` (validators_sequencers_nodes_oracles)
  Q: Which validators are Foundation-affiliated?
  why material: API gives names and stake, not control graph.
  closes if: Identity map.

- `HYPE-U-005` (tokenomics)
  Q: Free float / unlocks / insider inventory on as_of?
  why material: Staking threshold is not circulating supply.
  closes if: Date-aligned snapshot.

- `HYPE-U-006` (jurisdiction_legal)
  Q: Full legal map of Labs / Foundation / HPC?
  why material: Contributors page names Labs, not a registry.
  closes if: Primary filings.

- `HYPE-U-007` (smart_contracts)
  Q: Is HyperCore matching source public and reproducible?
  why material: Docs describe behaviour; they are not the binary.
  closes if: Public tree + build hash.

- `HYPE-U-008` (governance)
  Q: Can HYPE holders change HyperCore parameters without the validator path?
  why material: Quorum and jail are validator-set mechanics.
  closes if: Observed proposal → executed change without that path.

## stop

Investor decision sits outside this file.
