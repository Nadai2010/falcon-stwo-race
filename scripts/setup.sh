#!/usr/bin/env bash
# Build every side of every lane from public sources into build/ (see docs/setup.md).
#
#   HARNESS_DIR=/path/with/privacy_prove_stdout.rs,privacy_verify.rs,pvfast_workload_s1.rs  scripts/setup.sh
#
# Stwo trees: github.com/starknet-innovation/proving at the season commits, plus the record patches in patches/.
# The proof worker and verifier entry points (privacy_prove_stdout.rs, privacy_verify.rs) are the evaluator's
# own files that provably.fast gives participants for local measurement; they are not in the public fork, so
# point HARNESS_DIR at your copy. Falcon trees: OpenZeppelin/cairo-pq-verifiers at the baseline commit, plus
# the accepted record patch (MIT).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
B="$ROOT/build"
PROVING=https://github.com/starknet-innovation/proving
PQ=https://github.com/OpenZeppelin/cairo-pq-verifiers
S2=d6276445fc581908f10908294dc5c4638fc1766c   # season 2 pinned prover (100 provable bits)
S1=dd1787bc9                                  # season 1 base (unmodified prover)
OZ=bece5c07eeea5784e570c01108ec000d2d04ae40   # OpenZeppelin verifier baseline
: "${HARNESS_DIR:?set HARNESS_DIR to the folder holding privacy_prove_stdout.rs and privacy_verify.rs}"
mkdir -p "$B/inputs"

clone() { # url commit dir
  [ -d "$3/.git" ] || git clone -q "$1" "$3"
  git -C "$3" checkout -q --detach "$2"
}
apply_once() { # dir patch: apply unless it is already applied
  if git -C "$1" apply --reverse --check "$ROOT/patches/$2" 2>/dev/null; then echo "$(basename "$1"): $2 already applied"
  else git -C "$1" apply "$ROOT/patches/$2"; fi
}
stwo_tree() { # dir commit [patch]
  clone "$PROVING" "$2" "$B/$1"
  if [ -n "${3:-}" ]; then apply_once "$B/$1" "$3"; fi
  mkdir -p "$B/$1/crates/privacy_prove/src/bin"
  cp "$HARNESS_DIR/privacy_prove_stdout.rs" "$HARNESS_DIR/privacy_verify.rs" "$B/$1/crates/privacy_prove/src/bin/"
  # Season 1's commit has no proof body: the evaluator builds its default copy when a patch has none.
  local wl="$B/$1/crates/privacy_prove/src/pvfast_workload.rs"
  [ -f "$wl" ] || cp "$HARNESS_DIR/pvfast_workload_s1.rs" "$wl"
  (cd "$B/$1" && cargo build --release -q -p privacy-prove --bin privacy_prove_stdout --bin privacy_verify)
  echo "built $1"
}

stwo_tree stwo-pinned "$S2"
stwo_tree stwo-fast-record "$S2" stwo-fast-record-5eafa818.diff
stwo_tree stwo-s1-original "$S1"
stwo_tree stwo-s1-light-record "$S1" stwo-light-record-7bb39eeb.diff

# One fixed statement per season (a fresh random salt each time you run setup).
prep() { # tree out: written to a temporary name first, so an interrupted run never leaves a partial file
  local t="$B/$1" tmp="$2.tmp"
  [ -f "$2" ] && return 0
  (cd "$t" && cargo build --release -q -p privacy-prove --bin privacy_prepare_input)
  rm -f "$tmp"
  "$t/target/release/privacy_prepare_input" "$t/crates/privacy_prove/test_data/privacy_tx_cairo_pie.zip" \
    "$t/crates/cairo-program-runner-lib/resources/compiled_programs/test_programs/simple_output_compiled.json" \
    "$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')" "$tmp"
  mv "$tmp" "$2"
}
prep stwo-pinned "$B/inputs/s2_statement.json" || echo "note: prepare the season 2 statement with your provably.fast client"
prep stwo-s1-original "$B/inputs/s1_statement.json" || echo "note: prepare the season 1 statement with your provably.fast client"

clone "$PQ" "$OZ" "$B/falcon-oz-baseline"
clone "$PQ" "$OZ" "$B/falcon-record"
apply_once "$B/falcon-record" falcon-record-fj_97a86d12.patch
echo "setup done: make run (the Falcon trees compile on their first race)"
