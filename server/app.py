"""Local dashboard server: static page + race API. Stdlib only.

    python3 server/app.py            # http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import mimetypes
import signal
import sys
import threading
import time
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import race  # noqa: E402

WEB = race.ROOT / "web"
BUSY = threading.Lock()

# STRK/USD is always fetched live (never stored in the code): CoinGecko first, then Binance's STRKUSDT.
PRICE_SOURCES = (
    ("CoinGecko", "https://api.coingecko.com/api/v3/simple/price?ids=starknet&vs_currencies=usd",
     lambda d: float(d["starknet"]["usd"])),
    ("Binance", "https://api.binance.com/api/v3/ticker/price?symbol=STRKUSDT", lambda d: float(d["price"])),
)
PRICE_TTL_S = 60
_price_cache: dict = {}


def strk_usd() -> dict:
    now = time.time()
    if _price_cache and now - _price_cache["at"] < PRICE_TTL_S:
        return _price_cache["value"]
    for name, url, pick in PRICE_SOURCES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "falcon-stwo-race"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                value = {"usd": pick(json.load(resp)), "source": name, "fetched": int(now)}
            _price_cache.update(at=now, value=value)
            return value
        except (OSError, ValueError, KeyError):
            continue
    return {"usd": None, "source": None, "fetched": int(now)}


class Handler(BaseHTTPRequestHandler):
    server_version = "falcon-stwo-race"

    def log_message(self, fmt: str, *args) -> None:  # quiet console: one line per race only
        pass

    def _json(self, body: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _static(self, rel: str) -> None:
        path = (WEB / (rel or "index.html")).resolve()
        if WEB not in path.parents and path != WEB / "index.html" or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _local(self) -> bool:
        """Only this machine's own page may use the API: the Host must be loopback (no DNS rebinding) and a
        browser request must come from the same origin (no other site can start a race)."""
        port = self.server.server_address[1]
        if self.headers.get("Host") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
            return False
        return self.headers.get("Sec-Fetch-Site", "same-origin") in ("same-origin", "none")

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path.startswith("/api/") and not self._local():
            self._json({"error": "local page only"}, HTTPStatus.FORBIDDEN)
            return
        if url.path == "/api/price":
            self._json(strk_usd())
            return
        if url.path == "/api/status":
            self._json({"busy": BUSY.locked()})
            return
        if url.path == "/api/config":
            cfg = race.load_config()
            self._json({"lanes": [{k: v for k, v in lane.items() if k not in ("original", "record")}
                                  | {"original": {"label": lane["original"]["label"]},
                                     "record": {"label": lane["record"]["label"]}}
                                  for lane in cfg["lanes"]],
                        "missing": [k for k, v in cfg["paths"].items() if not Path(v).exists()]})
        elif url.path == "/api/race":
            self._race(parse_qs(url.query))
        else:
            self._static(url.path.lstrip("/"))

    def _race(self, query: dict) -> None:
        cfg = race.load_config()
        known = [lane["id"] for lane in cfg["lanes"]]
        lanes = [l for l in (query.get("lanes", [",".join(known)])[0]).split(",") if l in known]
        mode = query.get("mode", ["parallel"])[0]
        if mode not in ("parallel", "sequential") or not lanes:
            self._json({"error": "bad request"}, HTTPStatus.BAD_REQUEST)
            return
        if not BUSY.acquire(timeout=10):  # a stopped race may still be killing its provers
            self._json({"error": "a race is already running"}, HTTPStatus.CONFLICT)
            return
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            print(f"race: {','.join(lanes)} ({mode})", flush=True)
            gen = race.stream(cfg, lanes, mode)
            try:
                for ev in gen:
                    self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass  # browser closed or pressed stop: the generator's finally kills the provers
            finally:
                gen.close()
        finally:
            BUSY.release()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    signal.signal(signal.SIGTERM, lambda *_: (race.kill_all(), sys.exit(0)))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    print(f"falcon-stwo-race on http://127.0.0.1:{port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        race.kill_all()


if __name__ == "__main__":
    main()
