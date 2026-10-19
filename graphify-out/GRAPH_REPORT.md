# Graph Report - footnote  (2026-10-19)

## Corpus Check
- 28 files · ~46,848 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .diff 2, .patch 1)

## Summary
- 199 nodes · 285 edges · 18 communities (8 shown, 10 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5fe45c84`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- falcon-stwo-race
- app.js
- race.py
- mainnet_sim.mjs
- Race
- Handler
- falcon-stwo-race
- setup.sh
- clean-attribution-guard.test.sh
- STATUS archive (append-only, newest first)
- clean-attribution-guard.sh
- git-flow-guard.sh
- session-rules.sh
- ui.md
- workflow.md

## God Nodes (most connected - your core abstractions)
1. `Race` - 15 edges
2. `handle()` - 12 edges
3. `init()` - 9 edges
4. `start()` - 9 edges
5. `falcon-stwo-race` - 9 edges
6. `Handler` - 8 edges
7. `LaneError` - 7 edges
8. `_kill()` - 7 edges
9. `Side` - 7 edges
10. `reset()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Traps` --references--> `cpu_halves()`  [INFERRED]
  docs/STATUS.md → server/race.py
- `Events` --references--> `mainnet()`  [INFERRED]
  docs/architecture.md → web/app.js
- `Mainnet price` --references--> `mainnet()`  [INFERRED]
  docs/setup.md → web/app.js
- `main()` --calls--> `kill_all()`  [EXTRACTED]
  server/app.py → server/race.py

## Import Cycles
- None detected.

## Communities (18 total, 10 thin omitted)

### Community 0 - "falcon-stwo-race"
Cohesion: 0.06
Nodes (26): Architecture, Events, Process handling, Replay, Benchmarks: what each number means, Falcon-512, Fast prover (season 2), Honesty rules (+18 more)

### Community 1 - "app.js"
Cohesion: 0.20
Nodes (25): clearMainnet(), countUp(), css(), drawPlot(), fmt, handle(), init(), loadPeople() (+17 more)

### Community 2 - "race.py"
Cohesion: 0.06
Nodes (11): activity(), main(), main(), strk_usd(), cpu_halves(), expand(), kill_all(), load_config() (+3 more)

### Community 3 - "mainnet_sim.mjs"
Cohesion: 0.08
Nodes (15): bounds, boundsKey, cache, cfg, common, constructorCalldata, env, funder (+7 more)

### Community 4 - "Race"
Cohesion: 0.13
Nodes (7): _kill(), LaneError, Race, work(), Side, stream(), emit()

### Community 6 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (7): Agents (`.claude/agents/`), Commands, falcon-stwo-race, Finding code cheaply, Non-negotiable rules, Stack, Start here

### Community 8 - "setup.sh"
Cohesion: 0.73
Nodes (5): apply_once(), clone(), prep(), setup.sh script, stwo_tree()

### Community 10 - "STATUS archive (append-only, newest first)"
Cohesion: 0.33
Nodes (5): 2026-10-19: Fit-to-screen view and Built-on logos, 2026-10-19: Mainnet price in the Falcon card, quieter design, 2026-10-19: One-screen layout, 2026-10-19: Phase 1 done, STATUS archive (append-only, newest first)

## Knowledge Gaps
- **51 isolated node(s):** `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script`, `cfg`, `env` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 106 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cpu_halves()` connect `race.py` to `falcon-stwo-race`, `Race`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Why does `Traps` connect `falcon-stwo-race` to `race.py`?**
  _High betweenness centrality (0.235) - this node is a cross-community bridge._
- **What connects `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script` to the rest of the system?**
  _51 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `falcon-stwo-race` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `race.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059233449477351915 - nodes in this community are weakly interconnected._
- **Should `mainnet_sim.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `Race` be split into smaller, more focused modules?**
  _Cohesion score 0.12873563218390804 - nodes in this community are weakly interconnected._