# Benchmarks: what each number means

## Fast prover (season 2)
- Statement: one private transaction from the privacy pool test data, prepared once by `privacy_prepare_input`.
- Original: `starknet-innovation/proving` at `d6276445`, the season's pinned 100-provable-bit prover. Record: the same commit with the frontier patch (`5eafa818`, frontier `7a1b6eae`).
- Number: wall time of the whole process (setup included, as the evaluator times it). Both proofs must be accepted by the season's verifier, built from the pinned commit; they are byte-identical by the challenge's rules, so their size is shown equal.
- Official: 0.4992 of the pinned prover's time on the evaluator's 16-core AVX2 host (2026-10-18).

## Light prover (season 1)
- Original: `dd1787bc`, the unmodified prover. Record: the lowest measured peak of season 1, job `7bb39eeb`.
- Number: peak resident memory of the prover process (`VmHWM` live, the kernel's `ru_maxrss` at exit). Time is shown too; the light record is not tuned for speed.
- Official: 13.9 GiB to 1.04 GiB (season 1 summary on stwo.provably.fast).

## Falcon-512
- Original: OpenZeppelin's `Falcon512ShakeVerifier::verify` at `bece5c07`. Record: accepted job `fj_97a86d12`.
- Number: `l2_gas` of the repository's `bench_verify_falcon_512_shake` test (its genuine 9-block SHAKE-256 fixture), reported by Starknet Foundry 0.59.0. The board's score is the mean over 27 held-out signatures, 11 of them 8-block, so it is lower than this single fixture.
- Official: 27,915,721 against 48,398,466 gas, 1.73x (2026-10-18).

## Honesty rules
- Original and record always get the same input, parameters and thread budget.
- A number on screen is either produced by the run you are watching, or labelled as an official figure with its source and date, or part of a replay that says so.
- "Record" is the community's best tree, built on many people's work.
