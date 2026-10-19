#!/bin/bash
# Owner rule: clean history. No commit carries a "Co-Authored-By: Claude" trailer and no PR or issue carries the
# "Generated with Claude Code" signature. Overrides the harness default. PreToolUse(Bash): exit 2 blocks and tells Claude why.
CMD=$(jq -r '.tool_input.command // ""')
AT='(^|[;&|(]|\$\()[[:space:]]*'
MF=$(grep -oE -- "(-F|--file)[= ]+[^ ;&|]+" <<<"$CMD" | head -1 | sed -E 's/^(-F|--file)[= ]+//')
MSG=""; [ -n "$MF" ] && [ "$MF" != "-" ] && [ -f "$MF" ] && MSG=$(cat "$MF")
if grep -qE "${AT}git([[:space:]]+-C[[:space:]]+[^ ]+)?([[:space:]]+-c[[:space:]]+[^ ]+)*[[:space:]]+commit" <<<"$CMD" && grep -qiE "co-authored-by:[[:space:]]*claude" <<<"$CMD$MSG"; then
  echo "BLOCKED (owner rule): clean commits, no 'Co-Authored-By: Claude' line. Remove it and retry." >&2
  exit 2
fi
BF=$(grep -oE -- "(--body-file|-F)[= ]+[^ ;&|]+" <<<"$CMD" | head -1 | sed -E 's/^(--body-file|-F)[= ]+//')
BODY=""; [ -n "$BF" ] && [ -f "$BF" ] && BODY=$(cat "$BF")
if grep -qE "${AT}gh (pr|issue) (create|edit|comment)" <<<"$CMD" && grep -qiE "generated with \[?claude code" <<<"$CMD$BODY"; then
  echo "BLOCKED (owner rule): clean PRs and issues, no 'Generated with Claude Code' signature. Remove it and retry." >&2
  exit 2
fi
exit 0
