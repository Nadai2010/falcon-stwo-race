# Graph Report - mainnet  (2026-10-19)

## Corpus Check
- 28 files · ~46,466 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .diff 2, .patch 1)

## Summary
- 188 nodes · 271 edges · 20 communities (9 shown, 11 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9ded6edd`
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
- cpu_halves
- setup.sh
- clean-attribution-guard.test.sh
- STATUS archive (append-only, newest first)
- clean-attribution-guard.sh
- git-flow-guard.sh
- session-rules.sh
- ui.md
- workflow.md
- read_status

## God Nodes (most connected - your core abstractions)
1. `Race` - 14 edges
2. `handle()` - 12 edges
3. `init()` - 9 edges
4. `start()` - 9 edges
5. `falcon-stwo-race` - 9 edges
6. `Handler` - 8 edges
7. `LaneError` - 7 edges
8. `_kill()` - 7 edges
9. `Side` - 7 edges
10. `falcon-stwo-race` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Events` --references--> `mainnet()`  [INFERRED]
  docs/architecture.md → web/app.js
- `Mainnet price` --references--> `mainnet()`  [INFERRED]
  docs/setup.md → web/app.js
- `Traps` --references--> `cpu_halves()`  [INFERRED]
  docs/STATUS.md → server/race.py
- `main()` --calls--> `kill_all()`  [EXTRACTED]
  server/app.py → server/race.py

## Import Cycles
- None detected.

## Communities (20 total, 11 thin omitted)

### Community 0 - "falcon-stwo-race"
Cohesion: 0.07
Nodes (22): Architecture, Events, Process handling, Replay, Benchmarks: what each number means, Falcon-512, Fast prover (season 2), Honesty rules (+14 more)

### Community 1 - "app.js"
Cohesion: 0.21
Nodes (24): countUp(), css(), drawPlot(), fmt, handle(), init(), loadPeople(), mainnet() (+16 more)

### Community 2 - "race.py"
Cohesion: 0.07
Nodes (7): activity(), main(), main(), expand(), kill_all(), load_config(), mainnet_ready()

### Community 3 - "mainnet_sim.mjs"
Cohesion: 0.12
Nodes (12): bounds, cfg, common, constructorCalldata, env, funder, funderNonce, material (+4 more)

### Community 4 - "Race"
Cohesion: 0.15
Nodes (6): _kill(), LaneError, Race, Side, stream(), emit()

### Community 6 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (7): Agents (`.claude/agents/`), Commands, falcon-stwo-race, Finding code cheaply, Non-negotiable rules, Stack, Start here

### Community 7 - "cpu_halves"
Cohesion: 0.29
Nodes (6): OPEN, Project index: read this before doing anything, STATUS (single source of truth), Traps, cpu_halves(), parse_cpulist()

### Community 8 - "setup.sh"
Cohesion: 0.73
Nodes (5): apply_once(), clone(), prep(), setup.sh script, stwo_tree()

### Community 10 - "STATUS archive (append-only, newest first)"
Cohesion: 0.33
Nodes (5): 2026-10-19: Fit-to-screen view and Built-on logos, 2026-10-19: Mainnet price in the Falcon card, quieter design, 2026-10-19: One-screen layout, 2026-10-19: Phase 1 done, STATUS archive (append-only, newest first)

## Knowledge Gaps
- **48 isolated node(s):** `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script`, `cfg`, `env` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 98 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cpu_halves()` connect `cpu_halves` to `race.py`, `Race`?**
  _High betweenness centrality (0.256) - this node is a cross-community bridge._
- **Why does `STATUS (single source of truth)` connect `cpu_halves` to `falcon-stwo-race`?**
  _High betweenness centrality (0.254) - this node is a cross-community bridge._
- **What connects `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `falcon-stwo-race` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `race.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07226890756302522 - nodes in this community are weakly interconnected._
- **Should `mainnet_sim.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `Race` be split into smaller, more focused modules?**
  _Cohesion score 0.1452991452991453 - nodes in this community are weakly interconnected._