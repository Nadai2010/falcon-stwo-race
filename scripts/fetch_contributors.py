#!/usr/bin/env python3
"""Snapshot provably.fast's public participation table into web/data/contributors.json.

Only people with consented public activity are listed (the table's own scope). Ordered by total
activity: leads, builds, reproductions, sources, threads and replies.
"""
import datetime
import json
import urllib.request
from pathlib import Path

URL = "https://provably.fast/api/participation/people"
OUT = Path(__file__).resolve().parent.parent / "web" / "data" / "contributors.json"


def activity(p: dict) -> int:
    g, d = p.get("graph", {}), p.get("discussion", {})
    return sum(g.get(k, 0) for k in ("leads", "builds", "tested", "sources")) + d.get("threads", 0) + d.get("replies", 0)


def main() -> None:
    req = urllib.request.Request(URL, headers={"User-Agent": "falcon-stwo-race/0.1 (+https://github.com/Nadai2010/falcon-stwo-race)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    people = [{"login": p["login"], "user_id": p["user_id"], "activity": activity(p)}
              for p in data["people"] if p.get("login") and p.get("user_id")]
    people.sort(key=lambda p: (-p["activity"], p["login"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"fetched": datetime.date.today().isoformat(), "source": URL, "people": people}, indent=1) + "\n")
    print(f"{len(people)} contributors -> {OUT}")


if __name__ == "__main__":
    main()
