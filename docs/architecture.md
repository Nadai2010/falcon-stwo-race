# Architecture

```
browser (web/)                      server/app.py (stdlib)                 server/race.py
GET /api/config ───────────────▶   lanes from races.json, missing paths
GET /api/race?mode=… (SSE) ────▶   one race at a time (lock) ──────────▶  Race.run(lanes)
   ◀── data: {event} ────────────  streams events as they happen          per lane: spawn original + record,
                                                                           poll /proc/<pid>/status every 100 ms,
                                                                           verify proofs / parse snforge gas
```

## Events

| type | fields | meaning |
|---|---|---|
| `lane` | `lane`, `state` (`running`, `finished`, `error`), `mode`, `threads` | lane boundaries |
| `tick` | `lane`, `side`, `t` (s), `rss`, `peak` (bytes) | live sample of a running side |
| `done` | `lane`, `side`, `t`, `peak`, `ok`, `tail` | the process exited (`tail` = last stderr on failure) |
| `verified` | `lane`, `side`, `ok`, `bytes` | the season's verifier accepted (or rejected) the proof |
| `gas` | `lane`, `side`, `gas`, `ok` | Sierra gas parsed from snforge's report |
| `end` | `cancelled` | race over |

## Process handling
- Each side runs in its own session (`setsid`), so Stop or a closed page kills the whole process group.
- Side-by-side mode pins each side to one half of the CPUs (`sched_setaffinity`) with `RAYON_NUM_THREADS` set to that half; sequential mode gives each side the whole machine (`RAYON_NUM_THREADS` = all usable CPUs), one after the other. The Falcon lane always runs both snforge tests side by side: gas is deterministic.
- Commands and paths come only from `races.json` and `config.local.json`; the request only picks lanes and mode.
- Proofs and preimages go to a temporary directory per race.

## Replay
`/?replay` feeds `web/data/sample-run.json` (a recorded event stream with its date and machine) through the same handler, with a banner saying it is a replay.
