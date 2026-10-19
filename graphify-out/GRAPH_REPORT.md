# Graph Report - stage  (2026-10-19)

## Corpus Check
- 26 files · ~81,279 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .diff 2, .patch 1)

## Summary
- 162 nodes · 230 edges · 17 communities (7 shown, 10 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78dd6c67`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- falcon-stwo-race
- app.js
- race.py
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
1. `Race` - 13 edges
2. `handle()` - 10 edges
3. `init()` - 9 edges
4. `falcon-stwo-race` - 9 edges
5. `Handler` - 8 edges
6. `start()` - 8 edges
7. `LaneError` - 7 edges
8. `drawPlot()` - 7 edges
9. `falcon-stwo-race` - 7 edges
10. `cpu_halves()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Traps` --references--> `cpu_halves()`  [INFERRED]
  docs/STATUS.md → server/race.py
- `main()` --calls--> `kill_all()`  [EXTRACTED]
  server/app.py → server/race.py

## Import Cycles
- None detected.

## Communities (17 total, 10 thin omitted)

### Community 0 - "falcon-stwo-race"
Cohesion: 0.07
Nodes (25): Architecture, Events, Process handling, Replay, Benchmarks: what each number means, Falcon-512, Fast prover (season 2), Honesty rules (+17 more)

### Community 1 - "app.js"
Cohesion: 0.20
Nodes (23): countUp(), css(), drawPlot(), fmt, handle(), init(), loadPeople(), niceStep() (+15 more)

### Community 2 - "race.py"
Cohesion: 0.06
Nodes (9): activity(), main(), main(), cpu_halves(), expand(), kill_all(), load_config(), parse_cpulist() (+1 more)

### Community 4 - "Race"
Cohesion: 0.15
Nodes (6): _kill(), LaneError, Race, Side, stream(), emit()

### Community 6 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (7): Agents (`.claude/agents/`), Commands, falcon-stwo-race, Finding code cheaply, Non-negotiable rules, Stack, Start here

### Community 8 - "setup.sh"
Cohesion: 0.73
Nodes (5): apply_once(), clone(), prep(), setup.sh script, stwo_tree()

### Community 10 - "STATUS archive (append-only, newest first)"
Cohesion: 0.50
Nodes (3): 2026-10-19: Fit-to-screen view and Built-on logos, 2026-10-19: Phase 1 done, STATUS archive (append-only, newest first)

## Knowledge Gaps
- **35 isolated node(s):** `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script`, `state`, `fmt` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 81 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cpu_halves()` connect `race.py` to `falcon-stwo-race`, `Race`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `Traps` connect `falcon-stwo-race` to `race.py`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **What connects `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `falcon-stwo-race` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Should `race.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0620782726045884 - nodes in this community are weakly interconnected._
- **Should `Race` be split into smaller, more focused modules?**
  _Cohesion score 0.14666666666666667 - nodes in this community are weakly interconnected._