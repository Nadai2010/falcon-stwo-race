# Workflow rules (loaded at every session start by .claude/hooks/session-rules.sh)
- Start every session by reading `docs/STATUS.md` (index + open work). Never duplicate a script or a doc that already exists.
- Every number on screen is MEASURED by the race itself, or labelled as the official board figure with its source. Never paste a number as if it were live.
- "Original" and "record" in a lane always run the SAME configuration (statement, security parameters, threads); if anything differs, the UI says so.
- Money is shown from a LIVE price only: STRK/USD comes from `/api/price` (CoinGecko, then Binance) at view time; never store or hard-code an exchange rate.
- Credit is collective: the record trees include earlier community work. Say "original vs record", never "we alone".
- Clean history: no `Co-Authored-By: Claude` trailer, no "Generated with Claude Code" signature (blocked by `.claude/hooks/clean-attribution-guard.sh`).
- No direct push to `main`: one `feat/*` branch per change, each in its own git worktree, merged by PR (blocked by `.claude/hooks/git-flow-guard.sh`).
- Before calling a change done: run `make check`, take a screenshot of the dashboard, and pass the `senior-dev-reviewer` and (for UI) `design-reviewer` agents.
- To find code without reading whole files, query the graph first: `graphify query "<question>"` on `graphify-out/graph.json` (rebuild with `graphify update .` after structural changes (AST only, no LLM)).
