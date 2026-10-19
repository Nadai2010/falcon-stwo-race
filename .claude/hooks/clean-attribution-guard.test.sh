#!/bin/bash
# Self-test for clean-attribution-guard.sh: run `bash .claude/hooks/clean-attribution-guard.test.sh`.
H="$(dirname "$0")/clean-attribution-guard.sh"; fail=0
t() { printf '{"tool_input":{"command":%s}}' "$(jq -Rn --arg c "$2" '$c')" | bash "$H" >/dev/null 2>&1; r=$?; [ "$r" = "$1" ] || { echo "FAIL ($r != $1): $2"; fail=1; }; }
t 2 'git commit -m "x

Co-Authored-By: Claude <noreply@anthropic.com>"'
t 0 'git commit -m "Add race server"'
t 2 'gh pr create --title x --body "Generated with [Claude Code](https://claude.com/claude-code)"'
t 0 'gh pr create --title x --body "Adds the dashboard"'
[ $fail = 0 ] && echo "clean-attribution-guard: all tests pass"; exit $fail
