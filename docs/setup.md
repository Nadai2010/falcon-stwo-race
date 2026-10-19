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
