"""Live board figures for the three cards, read from provably.fast's public APIs on every page load.

Each card says who holds the record now and whose record it beat. The speed figure follows the board's own
formula (stwo.provably.fast, v2.js): the 100-bit season starts from the 90-bit season's frontier, so a proof
is 1 / (ratio of the 90-bit frontier x ratio of the 100-bit result) times faster than Stwo's base. Nothing
here is stored: if a source cannot be read, the card keeps the labelled text of races.json.
"""
from __future__ import annotations

import json
import time
import urllib.request

RESULTS = "https://provably.fast/api/participation/internal/results"
FALCON = "https://provably.fast/api/participation/falcon/results"
CAMPAIGNS = "https://stwo.provably.fast/data/campaigns.json"
SEASON_90 = "stwo-privacy-provable-whole-proof-v1"
SEASON_100 = "stwo-privacy-provable-100-whole-proof-v1"
SEASON_MEMORY = "stwo-privacy-whole-proof-internal-v1"
TTL_S = 60
_cache: dict = {}


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "falcon-stwo-race"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.load(resp)


def _day(ms: int) -> str:
    return time.strftime("%-d %b", time.gmtime(ms / 1000))


def fast(results: dict) -> dict:
    seasons = {s["campaign_id"]: s for s in results["seasons"]}
    base = seasons[SEASON_90]["frontier"]["ratio"]
    season = seasons[SEASON_100]
    # The records, in order: every measured improvement that was faster than all before it.
    rows = sorted((r for r in season["results"] if r["status"] == "MEASURED_IMPROVEMENT"),
                  key=lambda r: r["evaluated_at"])
    records, best = [], None
    for r in rows:
        if best is None or r["ratio"] < best["ratio"]:
            records.append(r)
            best = r
    holder = min(records, key=lambda r: abs(r["ratio"] - season["frontier"]["ratio"]))
    beaten = records[records.index(holder) - 1] if records.index(holder) > 0 else None
    # "times" is the board's figure, since step two began at 90 provable bits; "vs_pinned" is against the
    # season's pinned 100-bit prover d6276445, which is what the fast lane races.
    out = {"times": 1 / (base * holder["ratio"]), "vs_pinned": 1 / holder["ratio"], "holder": holder["github_login"],
           "date": _day(holder["evaluated_at"]), "commit": season["frontier"]["commit"][:9]}
    if beaten:
        out["beat"] = {"holder": beaten["github_login"], "times": 1 / (base * beaten["ratio"])}
    return out


def falcon(data: dict) -> dict:
    rec, base = data["record"], data["baseline"]
    prior = sorted((r for r in data["records"] if r["job_id"] != rec["job_id"]
                    and r["score_l2_gas"] > rec["score_l2_gas"]), key=lambda r: r["score_l2_gas"])
    out = {"base_gas": base["score_l2_gas"], "gas": rec["score_l2_gas"], "times": rec["times_cheaper"],
           "holder": rec.get("github_login"), "date": _day(rec["finished_at"]), "n_records": len(data["records"])}
    if prior and prior[0].get("github_login"):
        out["beat"] = {"holder": prior[0]["github_login"], "gas": prior[0]["score_l2_gas"]}
    return out


def light(campaigns: dict) -> dict:
    c = next(c for c in campaigns["campaigns"] if c["campaign_id"] == SEASON_MEMORY)
    return {"status": c["status"], "closed": c.get("closed")}


def board() -> dict:
    now = time.time()
    if _cache and now - _cache["at"] < TTL_S:
        return _cache["value"]
    value: dict = {"fetched": int(now)}
    for key, url, pick in (("fast", RESULTS, fast), ("falcon", FALCON, falcon), ("light", CAMPAIGNS, light)):
        try:
            value[key] = pick(_get(url))
        except (OSError, ValueError, KeyError, StopIteration, ZeroDivisionError):
            value[key] = None
    _cache.update(at=now, value=value)
    return value


if __name__ == "__main__":
    print(json.dumps(board(), indent=2))
