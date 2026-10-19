# Graph Report - phase1  (2026-10-19)

## Corpus Check
- 25 files · ~56,977 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .diff 2, .patch 1)

## Summary
- 141 nodes · 184 edges · 19 communities (7 shown, 12 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6c034cb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Benchmarks: what each number means
- app.js
- race.py
- app.py
- Race
- Handler
- falcon-stwo-race
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
1. `Race` - 10 edges
2. `handle()` - 10 edges
3. `init()` - 8 edges
4. `falcon-stwo-race` - 8 edges
5. `Handler` - 7 edges
6. `falcon-stwo-race` - 7 edges
7. `start()` - 6 edges
8. `reset()` - 6 edges
9. `drawPlot()` - 6 edges
10. `Side` - 5 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (19 total, 12 thin omitted)

### Community 0 - "Benchmarks: what each number means"
Cohesion: 0.10
Nodes (16): Architecture, Events, Process handling, Replay, Benchmarks: what each number means, Falcon-512, Fast prover (season 2), Honesty rules (+8 more)

### Community 1 - "app.js"
Cohesion: 0.23
Nodes (20): countUp(), css(), drawPlot(), fmt, handle(), init(), loadPeople(), niceStep() (+12 more)

### Community 2 - "race.py"
Cohesion: 0.11
Nodes (4): cpu_halves(), expand(), load_config(), read_status()

### Community 4 - "Race"
Cohesion: 0.22
Nodes (4): Race, Side, stream(), emit()

### Community 6 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (7): Agents (`.claude/agents/`), Commands, falcon-stwo-race, Finding code cheaply, Non-negotiable rules, Stack, Start here

### Community 7 - "falcon-stwo-race"
Cohesion: 0.25
Nodes (8): Built together, falcon-stwo-race, How it works, License, Run it, Status, The three races, Why

### Community 8 - "setup.sh"
Cohesion: 0.80
Nodes (4): clone(), prep(), setup.sh script, stwo_tree()

## Knowledge Gaps
- **34 isolated node(s):** `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script`, `state`, `fmt` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 76 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Race` connect `Race` to `race.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `Handler` connect `Handler` to `app.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `falcon-stwo-race` connect `falcon-stwo-race` to `Benchmarks: what each number means`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `clean-attribution-guard.sh script`, `git-flow-guard.sh script`, `session-rules.sh script` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Benchmarks: what each number means` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `race.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._