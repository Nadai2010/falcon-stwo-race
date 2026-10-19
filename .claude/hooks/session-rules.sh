#!/bin/bash
# SessionStart: print the fixed rules (single source: .claude/rules/workflow.md) at start and after every compaction.
F="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}/.claude/rules/workflow.md"
echo "FIXED OWNER RULES (falcon-stwo-race), always, without being repeated:"
[ -f "$F" ] && grep -E "^- " "$F"
exit 0
