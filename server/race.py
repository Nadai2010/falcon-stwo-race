"""Race runner: start the original and the record of a lane and stream what they measure.

Every number the dashboard shows comes from here: wall time from a monotonic clock, peak memory from the
kernel's accounting of the prover process (VmHWM while it runs, ru_maxrss when it is reaped), verification
from the season's verifier, Sierra gas from snforge's report.
"""
from __future__ import annotations

import atexit
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
VERIFY_TIMEOUT_S = 300
GAS_RE = re.compile(r"\[PASS\][^\n]*bench_verify_falcon_512_shake \(.*?l2_gas: ~(\d+)")

Emit = Callable[[dict], None]


class LaneError(Exception):
    """A lane cannot run (missing build, failed spawn); reported to the UI as the lane's error."""


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


def parse_cpulist(text: str) -> set[int]:
    out: set[int] = set()
    for part in text.strip().split(","):
        if part:
            lo, _, hi = part.partition("-")
            out.update(range(int(lo), int(hi or lo) + 1))
    return out


def cpu_halves() -> tuple[set[int], set[int]]:
    """Two equal halves of the usable CPUs. On hybrid CPUs (performance + efficiency cores) each kind is
    split evenly, so neither side gets all the fast cores; otherwise CPUs are dealt alternately. An odd CPU
    out is left unused so both sides get the same count."""
    usable = os.sched_getaffinity(0)
    groups = []
    for kind in ("cpu_core", "cpu_atom"):
        try:
            groups.append(sorted(parse_cpulist(Path(f"/sys/devices/{kind}/cpus").read_text()) & usable))
        except OSError:
            pass
    if not groups or set().union(*map(set, groups)) != usable:
        groups = [sorted(usable)]
    a: list[int] = []
    b: list[int] = []
    for group in groups:
        a += group[0::2]
        b += group[1::2]
    n = min(len(a), len(b))
    if n == 0:
        raise LaneError("side-by-side mode needs at least two CPUs")
    return set(a[:n]), set(b[:n])


# Every live child, so that nothing survives the server (atexit, SIGTERM) or a cancelled race.
_LIVE: set[subprocess.Popen] = set()
_LIVE_LOCK = threading.Lock()


def _kill(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=5)
    except (subprocess.TimeoutExpired, ChildProcessError):
        pass


def kill_all() -> None:
    with _LIVE_LOCK:
        live = list(_LIVE)
    for proc in live:
        _kill(proc)


atexit.register(kill_all)


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
    """One run of one or more lanes. `cancel()` kills every process it started or is about to start."""

    def __init__(self, config: dict, emit: Emit, mode: str = "parallel"):
        self.config, self.emit, self.mode = config, emit, mode
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.procs: list[subprocess.Popen] = []
        runs = ROOT / "runs"
        self.workdir = Path(tempfile.mkdtemp(prefix="race-", dir=runs if runs.is_dir() else None))

    # -- process plumbing -------------------------------------------------------------------------------
    def _spawn(self, s: Side) -> None:
        if self.cancelled.is_set():
            raise LaneError("cancelled")
        if s.stdout_path is None:
            s.stdout_path = self.workdir / f"{s.lane}-{s.side}.out"
        cmd = (["taskset", "-c", ",".join(map(str, sorted(s.cpus)))] if s.cpus else []) + s.cmd
        # Files, not pipes: a chatty process (snforge compiling) must never block on a full pipe.
        with open(s.stdout_path, "wb") as out, open(self.workdir / f"{s.lane}-{s.side}.err", "wb") as err:
            with self.lock:
                if self.cancelled.is_set():
                    raise LaneError("cancelled")
                s.start = time.monotonic()
                try:
                    s.proc = subprocess.Popen(cmd, cwd=s.cwd, env=os.environ | s.env, stdout=out, stderr=err,
                                              start_new_session=True)
                except OSError as exc:
                    raise LaneError(f"cannot start {s.cmd[0]}: {exc.strerror}") from exc
                self.procs.append(s.proc)
                with _LIVE_LOCK:
                    _LIVE.add(s.proc)

    def cancel(self) -> None:
        with self.lock:
            self.cancelled.set()
            procs = list(self.procs)
        for proc in procs:
            if proc.returncode is None:
                _kill(proc)

    def _reap(self, s: Side) -> bool:
        """Reap the side if it exited: exact end time and the kernel's peak RSS (ru_maxrss)."""
        try:
            pid, status, usage = os.wait4(s.proc.pid, os.WNOHANG)
        except ChildProcessError:
            return True
        if pid == 0:
            return False
        s.seconds = round(time.monotonic() - s.start, 2)
        s.proc.returncode = os.waitstatus_to_exitcode(status)
        s.returncode = s.proc.returncode
        s.peak = max(s.peak, usage.ru_maxrss * 1024)
        with _LIVE_LOCK:
            _LIVE.discard(s.proc)
        return True

    def _watch(self, sides: list[Side]) -> None:
        """Poll until every side exits, streaming elapsed time and memory."""
        pending = list(sides)
        while pending and not self.cancelled.is_set():
            for s in list(pending):
                if not self._reap(s):
                    rss, hwm = read_status(s.proc.pid)
                    s.peak = max(s.peak, hwm)
                    self.emit({"type": "tick", "lane": s.lane, "side": s.side,
                               "t": round(time.monotonic() - s.start, 2), "rss": rss, "peak": s.peak})
                    continue
                err = (self.workdir / f"{s.lane}-{s.side}.err").read_text(errors="replace")
                s.output = "" if s.stdout_path.suffix == ".proof" else s.stdout_path.read_text(errors="replace")
                if s.returncode != 0:
                    s.output += "\n" + err
                pending.remove(s)
                self.emit({"type": "done", "lane": s.lane, "side": s.side, "t": s.seconds, "peak": s.peak,
                           "ok": s.returncode == 0, "tail": "" if s.returncode == 0 else s.output[-600:]})
            time.sleep(POLL_S)

    def _preflight(self, *paths: str) -> None:
        missing = [p for p in paths if not Path(p).exists()]
        if missing:
            raise LaneError("not built: " + ", ".join(missing))

    # -- lanes -------------------------------------------------------------------------------------------
    def _prover_lane(self, lane: dict) -> None:
        paths = self.config["paths"]
        statement = paths[lane["statement"]]
        self._preflight(statement, *(expand(lane[n][k][:1], paths)[0] for n in ("original", "record")
                                     for k in ("prove", "verify")))
        preimage = self.workdir / f"{lane['id']}-preimage.json"
        with open(statement, "rb") as fh:
            preimage.write_text(json.dumps(json.loads(fh.readline())["output_preimage"]))
        if self.mode == "parallel":
            a, b = cpu_halves()
            threads = len(a)
        else:
            a = b = None
            threads = len(os.sched_getaffinity(0))
        sides = [Side(lane["id"], name, expand(lane[name]["prove"], paths, {"statement": statement}),
                      env={"RAYON_NUM_THREADS": str(threads)}, cpus=cpus,
                      stdout_path=self.workdir / f"{lane['id']}-{name}.proof")
                 for name, cpus in (("original", a), ("record", b))]
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
            v = Side(lane["id"], f"{s.side}-verify", verify)
            self._spawn(v)
            try:
                v.proc.wait(timeout=VERIFY_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                _kill(v.proc)
            with _LIVE_LOCK:
                _LIVE.discard(v.proc)
            ok = v.stdout_path.read_text(errors="replace").startswith("PRIVACY_VERIFY\tACCEPTED")
            self.emit({"type": "verified", "lane": lane["id"], "side": s.side, "ok": ok,
                       "bytes": s.stdout_path.stat().st_size})

    def _falcon_lane(self, lane: dict) -> None:
        # Gas is deterministic, so both snforge runs always go side by side whatever the mode.
        paths = self.config["paths"]
        repos = [paths[lane[name]["repo"]] for name in ("original", "record")]
        self._preflight(*repos)
        if not shutil.which("snforge"):
            raise LaneError("snforge (Starknet Foundry) is not on PATH")
        sides = [Side(lane["id"], name, ["snforge", "test", lane["test"]], cwd=repo)
                 for name, repo in zip(("original", "record"), repos)]
        self.emit({"type": "lane", "lane": lane["id"], "state": "running", "mode": "parallel"})
        for s in sides:
            self._spawn(s)
        self._watch(sides)
        for s in sides:
            m = GAS_RE.search(s.output)
            self.emit({"type": "gas", "lane": lane["id"], "side": s.side, "gas": int(m.group(1)) if m else None,
                       "ok": bool(m) and s.returncode == 0})

    def run(self, lane_ids: list[str]) -> None:
        lanes = {l["id"]: l for l in self.config["lanes"]}
        try:
            for lid in lane_ids:
                if self.cancelled.is_set():
                    break
                lane = lanes[lid]
                try:
                    (self._falcon_lane if lane["kind"] == "gas" else self._prover_lane)(lane)
                    self.emit({"type": "lane", "lane": lid, "state": "finished"})
                except Exception as exc:  # any failure ends this lane cleanly and stops its processes
                    self.cancel_lane()
                    if not self.cancelled.is_set():
                        self.emit({"type": "lane", "lane": lid, "state": "error", "error": str(exc)})
        finally:
            self.emit({"type": "end", "cancelled": self.cancelled.is_set()})

    def cancel_lane(self) -> None:
        """Kill this race's processes without cancelling the race (a lane failed; later lanes may run)."""
        with self.lock:
            procs = list(self.procs)
        for proc in procs:
            if proc.returncode is None:
                _kill(proc)
                with _LIVE_LOCK:
                    _LIVE.discard(proc)


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
                if sent == len(events):
                    cond.wait(timeout=15)
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
        worker.join(timeout=VERIFY_TIMEOUT_S)
        shutil.rmtree(race.workdir, ignore_errors=True)
