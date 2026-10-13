"""Serve the tutorial locally (with HTTP Range support so video seeking works).

    python3 learning_resource/site/serve.py            # http://127.0.0.1:8765/site/
    python3 learning_resource/site/serve.py --port 9000 --host 0.0.0.0   # reachable from your LAN

Serves the whole learning_resource/ folder, because the site embeds ../videos, ../diagrams and ../scripts.
"""

import argparse
import http.server
import os
import re
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # learning_resource


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mp4": "video/mp4", ".srt": "text/plain; charset=utf-8", ".py": "text/plain; charset=utf-8",
                      ".md": "text/plain; charset=utf-8", ".usda": "text/plain; charset=utf-8",
                      ".svg": "image/svg+xml", ".json": "application/json"}

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/site/")
            self.end_headers()
            return
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().do_GET()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        start = int(m.group(1)) if m and m.group(1) else 0
        end = int(m.group(2)) if m and m.group(2) else size - 1
        if m and not m.group(1) and m.group(2):  # suffix range: last N bytes
            start, end = max(0, size - int(m.group(2))), size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def log_message(self, fmt, *args):  # quieter log: skip static assets
        if not re.search(r"\.(css|js|png|svg|json|woff2?)\b", self.path):
            super().log_message(fmt, *args)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    with Server((a.host, a.port), Handler) as s:
        print(f"Isaac Sim 6.1 tutorial: http://{'127.0.0.1' if a.host == '0.0.0.0' else a.host}:{a.port}/site/  (Ctrl+C to stop)")
        s.serve_forever()
