# falcon-stwo-race

Local dashboard that races original against record builds, live: a full Stwo proof at 100 provable bits, a light (low-memory) Stwo proof, and a Falcon-512 signature verification in Sierra gas. Public repository.

## Start here
- **`docs/STATUS.md`**: single source of truth (project index + open work + decisions). Done work moves to `docs/STATUS-archive.md`.
- `README.md` (what and why) · `docs/architecture.md` · `docs/benchmarks.md` (what each number means) · `docs/setup.md` (builds).

## Stack
Python 3 stdlib server (`server/`), one static page with no build step (`web/`), lanes defined in `races.json`, builds from public commits plus `patches/` via `scripts/setup.sh`.

## Agents (`.claude/agents/`)
- **senior-dev-reviewer**: correctness, process safety, measurement honesty. Run it before calling a change done.
- **design-reviewer**: judges the rendered page from screenshots, score /10 + fixes.
- **bench-integrity**: audits that both sides of every lane run the same configuration and that every number is measured or labelled.

## Non-negotiable rules
Single source: `.claude/rules/workflow.md` (printed at every session start by `.claude/hooks/session-rules.sh`); UI rules in `.claude/rules/ui.md`. What can be checked is blocked by the hooks in `.claude/hooks/` (clean attribution, no direct push to main).

## Commands
```
make run            # dashboard on http://127.0.0.1:8765  (/?replay = labelled replay of the sample run)
make setup          # build every lane into build/ (HARNESS_DIR=..., see docs/setup.md)
make check          # syntax checks + hook self-tests
make contributors   # refresh the contributors snapshot
```

## Finding code cheaply
`graphify-out/graph.json` holds the project graph: `graphify query "<question>"` before reading whole files; rebuild with `graphify update .` after structural changes (AST only, no LLM).
