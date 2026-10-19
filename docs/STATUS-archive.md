# STATUS archive (append-only, newest first)

## 2026-10-19: Phase 1 done
- Three live lanes (fast, light, Falcon) on one page, one button, SSE streaming from a stdlib server; labelled replay of a recorded run.
- First full run on an Intel Core Ultra 9 275HX (24 threads, 62 GiB): fast 29.25 s vs 15.80 s (1.85x, side by side), light 13.95 GiB vs 1.04 GiB (13.5x), Falcon 50,190,408 vs 29,020,575 gas (1.73x). All proofs verified.
- Contributors section from provably.fast's public participation table (19 people, GitHub avatars).
- Project workflow copied from the owner's agency setup: CLAUDE.md, STATUS index, rules, agents, hooks (clean attribution, no direct push to main).
- Agreed flow for phase 2 (from the owner, 2026-10-18): our prover makes each block proof, the Stwo verifier checks it on screen, proofs published for anyone to re-verify, optionally one Falcon-signed mainnet transaction anchoring the final proof hash.
