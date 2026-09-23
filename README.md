# Protocol Research Bot

Independent Protocol Forensic Profile runtime.

Not a rating. Not a buy/sell signal. Not a court-ready store.

```
CRYPTO / BLOCKCHAIN PROJECT
        ↓
source intake + capture provenance
        ↓
evidence extraction
        ↓
13-axis Protocol Forensic Profile
        ↓
validate + render
```

Law: `CONTRACT_V1.yaml` (`cosm.bot.contract/1.0.0`, frozen).

## V2

V1 remains frozen as `cosm.bot.contract/1.0.0`.
V2 is an opt-in extension: `cosm.bot.v2.extension/1.0.0`.

V2 adds:

- Identity Gate
- Bytecode ↔ Audit Linkage
- Incident Finding Index

See [`v2/README.md`](v2/README.md).

## Run

```
python3 engine/pipeline.py run HYPE
python3 engine/pipeline.py run AAVE
```

Packs live in `packs/{TICKER}/` (`pack.yaml`, `sources.yaml`, `extract.py`).
The engine does not name a protocol.

## Compatibility

The legacy `engine/hype_pipeline.py` entry point was removed.
Use `engine/pipeline.py` with the HYPE or AAVE pack.
Profile YAML is canonical.
Rendered Markdown and TEST_RESULT files are generated artifacts and are not tracked.

## Profiles in this repo

- `profiles/HYPE/` — reference profile (`BOT-HYPE-001` r3)
- `profiles/AAVE/` — transferability profile (`BOT-AAVE-001` r1)

UNKNOWN / NOT_PROVEN are valid outputs.
Missing data is not missing risk.

## Archive

`archive/2026-05-30/` is the previous public methodology pack.
It is not V1 runtime.

## Disclaimer

See `DISCLAIMER.md`.
