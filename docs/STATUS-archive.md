# STATUS archive (append-only, newest first)

## 2026-10-19: One-screen layout
- The fit-to-screen view is now the only layout: three cards side by side, run controls and contributors (colour avatar stack with names on hover) in a dock under the cards, a footnote on why numbers differ per machine and the non-affiliation disclaimer. Each card links to its provably.fast challenge; the header links to this repository.
- Owner decision: phase 2 (simulated L1 blocks) is dropped; next is a simple mainnet comparison of the two Falcon accounts.

## 2026-10-19: Fit-to-screen view and Built-on logos
- `F`, the header button or `/?stage`: the three lanes side by side on one 16:9 screen for recording (checked at 1920x1080 and 1440x900).
- Header: "Built on" Stwo (StarkWare) and Starknet with their GitHub organisation logos, plus a non-affiliation disclaimer in the footer and the README.
- README explains why a single live ratio moves a few percent between runs.

## 2026-10-19: Phase 1 done
- Three live lanes (fast, light, Falcon) on one page, one button, SSE streaming from a stdlib server; labelled replay of a recorded run.
- Recorded runs on an Intel Core Ultra 9 275HX (8P + 16E cores, 62 GiB), all proofs verified: side by side, fast 29.57 s vs 11.20 s, 2.64x, light 13.85 GiB vs 1.04 GiB, 13.4x, Falcon 50,190,408 vs 29,020,575 gas (1.73x); one after the other, fast 21.38 s vs 7.80 s, 2.74x, light 14.31 GiB vs 1.06 GiB, 13.5x. Both saved as labelled replays.
- Senior review fixes: Stop in sequential mode can no longer leave a prover running; any lane exception ends the race cleanly; provers die with the server (atexit, SIGTERM); replay never mixes into a live run; exact exit time and kernel peak (wait4); sequential mode uses every CPU; preflight of builds; verify timeout; API answers only to its own local page (Host, Origin, Sec-Fetch-Site); gas verdict requires both tests to pass; Ctrl+R no longer starts a race; idempotent patching in setup.
- Fixed: side-by-side mode first split CPUs 0-11 / 12-23, which gave the original all 8 performance cores; now each core type is split evenly.
- Contributors section from provably.fast's public participation table (19 people, GitHub avatars).
- Project workflow copied from the owner's agency setup: CLAUDE.md, STATUS index, rules, agents, hooks (clean attribution, no direct push to main).
- Agreed flow for phase 2 (from the owner, 2026-10-18): our prover makes each block proof, the Stwo verifier checks it on screen, proofs published for anyone to re-verify, optionally one Falcon-signed mainnet transaction anchoring the final proof hash.
