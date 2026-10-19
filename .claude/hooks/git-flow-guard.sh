#!/bin/bash
# Owner rule: no direct push to main. Work on feat/* branches (one git worktree per feature) and merge through a PR.
CMD=$(jq -r '.tool_input.command // ""')
if grep -qE '(^|[;&|(])[[:space:]]*git([[:space:]]+-C[[:space:]]+[^ ]+)?[[:space:]]+push([[:space:]]+[^;&|]*)?[[:space:]](origin[[:space:]]+)?(HEAD:)?main([[:space:]]|$)' <<<"$CMD"; then
  echo "BLOCKED (owner rule): no direct push to main. Push your feat/* branch and open a PR." >&2
  exit 2
fi
exit 0
