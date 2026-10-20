#!/usr/bin/env bash
# Keep the record side of the fast and Falcon lanes on the live frontiers (see docs/setup.md, "Staying in sync").
#
#   HARNESS_DIR=/path/with/privacy_prove_stdout.rs,privacy_verify.rs  scripts/sync_frontier.sh
#
# Fast lane: the head of starknet-innovation/proving's provable-100-season branch (the promoted frontier) against the
# prover step two began with (1d7c6f75, 90 provable bits), as the board measures its speed; the season's pinned
# prover is built too, for its 100-bit verifier. All with the evaluator's flags, so the race compares code, not
# compilers. Falcon lane: OpenZeppelin's baseline plus the current record's patch from the Falcon results API.
# Nothing is rebuilt when the frontier has not moved. build/frontier.json says what the lanes run; it is written
# only after every build succeeded, so a failed or interrupted sync leaves the previous builds in use.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
B="$ROOT/build"
PROVING=https://github.com/starknet-innovation/proving
PQ=https://github.com/OpenZeppelin/cairo-pq-verifiers
BRANCH=provable-100-season
S2=d6276445fc581908f10908294dc5c4638fc1766c   # season 2 pinned prover (100 provable bits): its verifier checks the record
START=1d7c6f752d286a765e4f551c976140c8ad7b024a # where step two began (90 provable bits): the board's speed is measured from it
OZ=bece5c07eeea5784e570c01108ec000d2d04ae40   # OpenZeppelin verifier baseline
FALCON_API=https://provably.fast/api/participation/falcon
export RUSTFLAGS="-C target-cpu=native -C opt-level=3 -C codegen-units=1"   # the evaluator's flags
if [ -z "${HARNESS_DIR:-}" ] && [ -f "$ROOT/config.local.json" ]; then
  HARNESS_DIR=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('harness_dir', ''))" "$ROOT/config.local.json")
fi
: "${HARNESS_DIR:?set HARNESS_DIR (or harness_dir in config.local.json) to the folder holding privacy_prove_stdout.rs}"
mkdir -p "$B"

mirror() { # url dir: one local mirror per upstream, checkouts are worktrees of it
  [ -d "$2" ] || git clone -q --bare "$1" "$2"
  git -C "$2" fetch -q origin '+refs/heads/*:refs/heads/*'
}
checkout() { # mirror commit dir
  [ -d "$3" ] || git -C "$1" worktree add -q --detach "$3" "$2"
}
stwo_build() { # commit dir
  checkout "$B/proving.git" "$1" "$2"
  mkdir -p "$2/crates/privacy_prove/src/bin"
  cp "$HARNESS_DIR/privacy_prove_stdout.rs" "$HARNESS_DIR/privacy_verify.rs" "$2/crates/privacy_prove/src/bin/"
  [ -x "$2/target/release/privacy_prove_stdout" ] && [ -x "$2/target/release/privacy_verify" ] && return 0
  (cd "$2" && nice -n 19 cargo build --release --locked -q -p privacy-prove --bin privacy_prove_stdout --bin privacy_verify)
}

mirror "$PROVING" "$B/proving.git"
FRONTIER=$(git -C "$B/proving.git" rev-parse "refs/heads/$BRANCH")
stwo_build "$S2" "$B/stwo-pinned-native"
stwo_build "$START" "$B/stwo-step2-start"
stwo_build "$FRONTIER" "$B/stwo-frontier-${FRONTIER:0:9}"

mirror "$PQ" "$B/pq.git"
RECORD=$(curl -fsS "$FALCON_API/results" | python3 -c "import json,sys; print(json.load(sys.stdin)['record']['job_id'])")
FDIR="$B/falcon-frontier-${RECORD:3:8}"
if [ ! -f "$FDIR/.record-applied" ]; then
  checkout "$B/pq.git" "$OZ" "$FDIR"
  curl -fsS "$FALCON_API/jobs/$RECORD/patch" -o "$FDIR/.record.patch"
  git -C "$FDIR" apply "$FDIR/.record.patch"
  echo "$RECORD" > "$FDIR/.record-applied"
fi

python3 - "$B" "$FRONTIER" "$RECORD" "$FDIR" <<'EOF'
import json, os, sys, time
b, frontier, record, fdir = sys.argv[1:]
out = {
    "synced": int(time.time()),
    "fast": {"commit": frontier, "start": f"{b}/stwo-step2-start", "pinned": f"{b}/stwo-pinned-native",
             "record": f"{b}/stwo-frontier-{frontier[:9]}"},
    "falcon": {"job": record, "record": fdir},
}
tmp = f"{b}/frontier.json.tmp"
with open(tmp, "w") as f:
    json.dump(out, f, indent=2)
os.replace(tmp, f"{b}/frontier.json")
EOF
echo "in sync: fast ${FRONTIER:0:9}, falcon $RECORD"
