# Graph Report - phase1  (2026-10-19)

## Corpus Check
- 26 files · ~60,342 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .diff 2, .patch 1)

## Summary
- 159 nodes · 224 edges · 18 communities (7 shown, 11 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0dbaa72a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- falcon-stwo-race
- app.js
- race.py
- app.py
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
3. `Handler` - 8 edges
4. `init()` - 8 edges
5. `start()` - 8 edges
6. `falcon-stwo-race` - 8 edges
7. `LaneError` - 7 edges
8. `falcon-stwo-race` - 7 edges
9. `cpu_halves()` - 6 edges
10. `_kill()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Traps` --references--> `cpu_halves()`  [INFERRED]
  docs/STATUS.md → server/race.py
- `main()` --calls--> `kill_all()`  [EXTRACTED]
  server/app.py → server/race.py

## Import Cycles
- None detected.

## Communities (18 total, 11 thin omitted)

### Community 0 - "falcon-stwo-race"
Cohesion: 0.07
Nodes (24): Architecture, Events, Process handling, Replay, Benchmarks: what each number means, Falcon-512, Fast prover (season 2), Honesty rules (+16 more)

### Community 1 - "app.js"
Cohesion: 0.21
Nodes (22): countUp(), css(), drawPlot(), fmt, handle(), init(), loadPeople(), niceStep() (+14 more)

### Community 2 - "race.py"
Cohesion: 0.11
Nodes (5): cpu_halves(), expand(), load_config(), parse_cpulist(), read_status()

### Community 3 - "app.py"
Cohesion: 0.12
Nodes (4): activity(), main(), main(), kill_all()

### Community 4 - "Race"
Cohesion: 0.15
Nodes (6): _kill(), LaneError, Race, Side, stream(), emit()

### Community 6 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (7): Agents (`.claude/agents/`), Commands, falcon-stwo-race, Finding code cheaply, Non-negotiable rules, Stack, Start here

### Community 8 - "setup.sh"
Cohesion: 0.73
Nodes (5): apply_once(), clone(), prep(), setup.sh script, stwo_tree()

## Knowledge Gaps
- **33 isolated node(s):** `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script`, `state`, `fmt` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 79 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cpu_halves()` connect `race.py` to `falcon-stwo-race`, `Race`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `Traps` connect `falcon-stwo-race` to `race.py`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **What connects `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script` to the rest of the system?**
  _33 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `falcon-stwo-race` be split into smaller, more focused modules?**
  _Cohesion score 0.06896551724137931 - nodes in this community are weakly interconnected._
- **Should `race.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11695906432748537 - nodes in this community are weakly interconnected._
- **Should `Race` be split into smaller, more focused modules?**
  _Cohesion score 0.14666666666666667 - nodes in this community are weakly interconnected._