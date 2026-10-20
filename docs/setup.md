# Setup

`make setup` (= `scripts/setup.sh`) builds the four Stwo trees and checks out and patches the two Falcon trees in `build/` (Starknet Foundry compiles those on their first race):

| Tree | Source | Patch |
|---|---|---|
| `stwo-pinned` | starknet-innovation/proving `d6276445` (season 2 pin, 100 provable bits) | none |
| `stwo-fast-record` | same commit | `patches/stwo-fast-record-5eafa818.diff` (= frontier `7a1b6eae`) |
| `stwo-s1-original` | starknet-innovation/proving `dd1787bc` (season 1 base) | none |
| `stwo-s1-light-record` | same commit | `patches/stwo-light-record-7bb39eeb.diff` |
| `falcon-oz-baseline` | OpenZeppelin/cairo-pq-verifiers `bece5c07` | none |
| `falcon-record` | same commit | `patches/falcon-record-fj_97a86d12.patch` (accepted record, MIT) |

It also prepares one fixed statement per season in `build/inputs/` with `privacy_prepare_input`.

## HARNESS_DIR

The proof worker and verifier entry points (`crates/privacy_prove/src/bin/privacy_prove_stdout.rs`, `privacy_verify.rs`) belong to the provably.fast evaluator and are not part of the public fork; season 1's commit also has no default proof body (`pvfast_workload_s1.rs`). Put those three files in one folder and pass it as `HARNESS_DIR`. Every side of every lane uses the same copies, so the comparison stays fair.

## Using existing builds

Create `config.local.json` (ignored by git) with a `paths` object overriding any key of `races.json`'s `paths`; the dashboard lists missing paths at the top of the page.

## Mainnet price

The Falcon card prices one Falcon-signed transaction per account on Starknet mainnet by simulation (`server/mainnet_sim.mjs`); nothing is broadcast or paid. To run it live, add a `mainnet` object to `config.local.json`:

```json
"mainnet": {
  "env": "/private/path/.env",
  "rpc": "https://api.zan.top/public/starknet-mainnet/rpc/v0_10",
  "cli": "/path/to/cairo-pq-verifiers/pq-accounts/cli",
  "falcon_py": "/path/to/falcon.py",
  "falcon_key": "/private/path/falcon-key.json",
  "sides": { "original": "/path/to/oz-tree", "record": "/path/to/record-tree" }
}
```

- `env` holds `PQ_RPC`, `PQ_FUNDER_ADDRESS` and `PQ_FUNDER_PRIVATE_KEY` of any funded mainnet account; it signs the simulated declares and is never sent anywhere else. Keep it outside the repository.
- `rpc` must accept multi-megabyte requests: the record's account class is 3.1 MB, which Alchemy and publicnode refuse; ZAN's public endpoint accepts it.
- `cli` is OpenZeppelin's `pq-accounts/cli` with `npm ci && npm run build` done; `sides` are the two verifier trees with `scarb build -p pq_accounts` done.
- `falcon_key` can be any Falcon key (`falcon_signer.py keygen`): nothing is broadcast.

Without this block the card shows `web/data/mainnet-sim.json`, the last recorded simulation.


## Staying in sync with the live frontiers

`scripts/sync_frontier.sh` keeps the record side of the fast and Falcon lanes on the current records: the head of
`starknet-innovation/proving`'s `provable-100-season` branch (the promoted frontier) and the Falcon record's patch from
the Falcon results API. The fast lane's pinned prover is rebuilt beside it with the evaluator's flags
(`-C target-cpu=native -C opt-level=3 -C codegen-units=1`), so both sides of the race use the same compiler settings.
The server runs the script in the background when it starts and, at most every 15 minutes, when the page loads; a
race asked for while it builds is refused with a note. It reads the harness files from `HARNESS_DIR` or from
`"harness_dir"` in `config.local.json`, writes `build/frontier.json` only after every build succeeded, and the lanes
use those builds from then on (the side labels name the frontier commit and its holder).
