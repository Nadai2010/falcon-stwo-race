"""Race runner: start the original and the record of a lane side by side and stream what they measure.

Every number the dashboard shows comes from here: wall time from a monotonic clock, peak memory from the
prover's own VmHWM in /proc, verification from the verifier's verdict, Sierra gas from snforge's report.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

ROOT = Path(__file__).resolve().parent.parent
POLL_S = 0.1
GAS_RE = re.compile(r"bench_verify_falcon_512_shake \(.*?l2_gas: ~(\d+)")

Emit = Callable[[dict], None]


def load_config() -> dict:
    """races.json, with paths taken from config.local.json when present (see docs/setup.md)."""
    races = json.loads((ROOT / "races.json").read_text())
    local = ROOT / "config.local.json"
    paths = races["paths"] | (json.loads(local.read_text()).get("paths", {}) if local.exists() else {})
    races["paths"] = {k: str((ROOT / v).resolve()) if not os.path.isabs(v) else v for k, v in paths.items()}
    return races


def expand(template: list[str], paths: dict, extra: dict | None = None) -> list[str]:
    values = paths | (extra or {})
    return [re.sub(r"\{(\w+)\}", lambda m: values[m.group(1)], part) for part in template]


def read_status(pid: int) -> tuple[int, int]:
    """(VmRSS, VmHWM) in bytes for a live process, or (0, 0) once it is gone."""
    try:
        text = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return 0, 0
    def kb(key: str) -> int:
        m = re.search(rf"^{key}:\s+(\d+) kB", text, re.M)
        return int(m.group(1)) * 1024 if m else 0
    return kb("VmRSS"), kb("VmHWM")


def cpu_halves() -> tuple[set[int], set[int]]:
    cpus = sorted(os.sched_getaffinity(0))
    half = len(cpus) // 2
    return set(cpus[:half]), set(cpus[half:])


@dataclass
class Side:
    lane: str
    side: str
    cmd: list[str]
    cwd: str | None = None
    env: dict = field(default_factory=dict)
    cpus: set[int] | None = None
    stdout_path: Path | None = None
    proc: subprocess.Popen | None = None
    start: float = 0.0
    seconds: float | None = None
    peak: int = 0
    returncode: int | None = None
    output: str = ""


class Race:
    """One run of one or more lanes. `cancel()` kills every process it started."""

    def __init__(self, config: dict, emit: Emit, mode: str = "parallel"):
        self.config, self.emit, self.mode = config, emit, mode
        self.sides: list[Side] = []
        self.cancelled = threading.Event()
        self.workdir = Path(tempfile.mkdtemp(prefix="race-", dir=ROOT / "runs" if (ROOT / "runs").exists() else None))

    # -- process plumbing -------------------------------------------------------------------------------
    def _spawn(self, s: Side) -> None:
        env = os.environ | s.env
        # Files, not pipes: a chatty process (snforge compiling) must never block on a full pipe.
        if s.stdout_path is None:
            s.stdout_path = self.workdir / f"{s.lane}-{s.side}.out"
        out = open(s.stdout_path, "wb")
        err = open(self.workdir / f"{s.lane}-{s.side}.err", "wb")
        cpus = s.cpus
        def pre() -> None:
            os.setsid()
            if cpus:
                os.sched_setaffinity(0, cpus)
        s.start = time.monotonic()
        s.proc = subprocess.Popen(s.cmd, cwd=s.cwd, env=env, stdout=out, stderr=err, preexec_fn=pre)
        out.close()
        err.close()
        self.sides.append(s)

    def cancel(self) -> None:
        self.cancelled.set()
        for s in self.sides:
            if s.proc and s.proc.poll() is None:
                try:
                    os.killpg(s.proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def _watch(self, sides: list[Side]) -> None:
        """Poll until every side exits, streaming elapsed time and memory."""
        pending = list(sides)
        while pending and not self.cancelled.is_set():
            for s in list(pending):
                rss, hwm = read_status(s.proc.pid)
                s.peak = max(s.peak, hwm)
                rc = s.proc.poll()
                now = time.monotonic() - s.start
                if rc is None:
                    self.emit({"type": "tick", "lane": s.lane, "side": s.side, "t": round(now, 2),
                               "rss": rss, "peak": s.peak})
                    continue
                s.seconds, s.returncode = round(now, 2), rc
                err = (self.workdir / f"{s.lane}-{s.side}.err").read_text(errors="replace")
                s.output = "" if s.stdout_path.suffix == ".proof" else s.stdout_path.read_text(errors="replace")
                if rc != 0:
                    s.output += "\n" + err
                pending.remove(s)
                self.emit({"type": "done", "lane": s.lane, "side": s.side, "t": s.seconds, "peak": s.peak,
                           "ok": rc == 0, "tail": "" if rc == 0 else s.output[-600:]})
            time.sleep(POLL_S)

    # -- lanes -------------------------------------------------------------------------------------------
    def _prover_lane(self, lane: dict) -> None:
        paths = self.config["paths"]
        statement = paths[lane["statement"]]
        preimage = self.workdir / f"{lane['id']}-preimage.json"
        with open(statement, "rb") as fh:
            preimage.write_text(json.dumps(json.loads(fh.readline())["output_preimage"]))
        a, b = cpu_halves() if self.mode == "parallel" else (None, None)
        threads = str(len(a)) if a else lane.get("threads", "16")
        sides = []
        for name, cpus in (("original", a), ("record", b)):
            spec = lane[name]
            sides.append(Side(lane["id"], name, expand(spec["prove"], paths, {"statement": statement}),
                              env={"RAYON_NUM_THREADS": threads}, cpus=cpus,
                              stdout_path=self.workdir / f"{lane['id']}-{name}.proof"))
        self.emit({"type": "lane", "lane": lane["id"], "state": "running", "mode": self.mode, "threads": threads})
        if self.mode == "parallel":
            for s in sides:
                self._spawn(s)
            self._watch(sides)
        else:
            for s in sides:
                self._spawn(s)
                self._watch([s])
        for s in sides:
            if self.cancelled.is_set() or s.returncode != 0:
                continue
            verify = expand(lane[s.side]["verify"], paths, {"proof": str(s.stdout_path), "preimage": str(preimage)})
            done = subprocess.run(verify, capture_output=True, text=True)
            ok = done.stdout.startswith("PRIVACY_VERIFY\tACCEPTED")
            self.emit({"type": "verified", "lane": lane["id"], "side": s.side, "ok": ok,
                       "bytes": s.stdout_path.stat().st_size})

    def _falcon_lane(self, lane: dict) -> None:
        paths = self.config["paths"]
        sides = [Side(lane["id"], name, ["snforge", "test", lane["test"]], cwd=paths[lane[name]["repo"]])
                 for name in ("original", "record")]
        self.emit({"type": "lane", "lane": lane["id"], "state": "running", "mode": "parallel"})
        for s in sides:
            self._spawn(s)
        self._watch(sides)
        for s in sides:
            m = GAS_RE.search(s.output)
            self.emit({"type": "gas", "lane": lane["id"], "side": s.side, "gas": int(m.group(1)) if m else None,
                       "ok": bool(m) and "[PASS]" in s.output})

    def run(self, lane_ids: list[str]) -> None:
        lanes = {l["id"]: l for l in self.config["lanes"]}
        for lid in lane_ids:
            if self.cancelled.is_set():
                break
            lane = lanes[lid]
            try:
                (self._falcon_lane if lane["kind"] == "gas" else self._prover_lane)(lane)
                self.emit({"type": "lane", "lane": lid, "state": "finished"})
            except (OSError, KeyError, ValueError) as exc:
                self.emit({"type": "lane", "lane": lid, "state": "error", "error": str(exc)})
        self.emit({"type": "end", "cancelled": self.cancelled.is_set()})


def stream(config: dict, lane_ids: list[str], mode: str) -> Iterator[dict]:
    """Run a race in a thread and yield its events; closing the generator cancels the race."""
    events: list[dict] = []
    cond = threading.Condition()
    def emit(ev: dict) -> None:
        with cond:
            events.append(ev)
            cond.notify()
    race = Race(config, emit, mode)
    worker = threading.Thread(target=race.run, args=(lane_ids,), daemon=True)
    worker.start()
    sent = 0
    try:
        while True:
            with cond:
                while sent == len(events):
                    cond.wait(timeout=15)
                    if sent == len(events):
                        break
                batch, sent = events[sent:], len(events)
            if not batch:
                yield {"type": "ping"}
                continue
            for ev in batch:
                yield ev
                if ev["type"] == "end":
                    return
    finally:
        race.cancel()
        worker.join(timeout=5)
        shutil.rmtree(race.workdir, ignore_errors=True)
