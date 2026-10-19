"""Local dashboard server: static page + race API. Stdlib only.

    python3 server/app.py            # http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import mimetypes
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import race  # noqa: E402

WEB = race.ROOT / "web"
BUSY = threading.Lock()


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

    def do_GET(self) -> None:
        url = urlparse(self.path)
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
        if not BUSY.acquire(blocking=False):
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
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    print(f"falcon-stwo-race on http://127.0.0.1:{port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
