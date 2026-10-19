# STATUS (single source of truth)

## Project index: read this before doing anything

| I need | Go to |
|---|---|
| What this is, rules, agents, commands | `CLAUDE.md` |
| What is OPEN now | this file, table below |
| What is DONE (append-only log, newest first) | `docs/STATUS-archive.md` + git history |
| Architecture (server, SSE events, process handling) | `docs/architecture.md` |
| What each number means and how it is measured | `docs/benchmarks.md` |
| How the builds are made | `docs/setup.md`, `scripts/setup.sh`, `patches/` |
| Lane definitions (commands, labels, official figures) | `races.json` |
| Find a function without reading files | `graphify query "..."` on `graphify-out/graph.json` |

Golden rules: reuse before creating (one canonical doc per topic, one script per task); every number measured or labelled with its source; if a request is unclear, ask.

Rule: when an item is DONE it leaves this table and is appended to `docs/STATUS-archive.md`.

## OPEN

| # | Item | State | Notes |
|---|---|---|---|
| 1 | Decide repository visibility and license | 🔴 owner | Private for now; MIT proposed in LICENSE (patches follow upstream licenses). |
| 2 | Public source for the evaluator's proof-worker entry points | 🔴 | `privacy_prove_stdout.rs`, `privacy_verify.rs` and season 1's default `pvfast_workload.rs` are not in the public fork; `make setup` needs `HARNESS_DIR`. Ask the maintainers whether they can be published, or document how participants obtain them. |
| 3 | Pending Falcon records | 🟡 waiting | Two cheaper Falcon trees are ready (local 9-block fixture 27,748,819 and 27,493,491 gas); swap `falcon_record_repo` and the patch once one becomes the official record. |
| 4 | Mainnet: OpenZeppelin Falcon account vs record account | 🟡 | Simulated on mainnet at zero cost (2026-10-19): one Falcon-signed transaction costs 0.823 STRK (53.5M L2 gas) with OpenZeppelin's account and 0.499 STRK (32.3M) with the record's, 1.65x cheaper; declares 66.5 and 83.8 STRK. Shown in the Falcon card (live simulation after each race, or the last one). Declaring for real only once the Falcon record is final: any change to the verifier is a new class to declare again (owner, 2026-10-19). |
| 7 | Video montage | 🔴 | Starts in black, fast story of what was achieved, then the live demo (owner, 2026-10-19). |
| 5 | Show build identity on each side | 🔴 | `/api/config` could report a sha256 / `git describe` per binary and tree so the labels in `races.json` are checked, not trusted (senior review, 2026-10-19). |
| 6 | One-button "submit the improvements" | 🔴 idea | Owner idea: a button that also pushes pending improvements; needs a design that never submits without an explicit confirmation. |

## Traps
- The original light prover needs about 14 GiB of free memory; on smaller machines it fails and the lane says so.
- Side-by-side mode halves the cores per side. On hybrid CPUs each core type is split evenly (`cpu_halves`); a naive half split once gave one side all the performance cores.
- Local Intel ratios for the fast lane (2.6x to 2.9x) are higher than the board's 2.0x on the evaluator's Zen 3 host; always show both.
- Peak memory of the original light prover varies run to run (13.4 to 14.3 GiB here).
- snforge compiles on first run; the first Falcon race takes longer than later ones.
