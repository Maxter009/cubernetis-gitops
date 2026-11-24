"""Kleine Demo-App: meldet Version, Farbe und Pod-Namen.

Version und Farbe werden beim Image-Build fest eingebacken (Build-Args),
damit ein Versionswechsel wie in echt nur ueber ein neues Image-Tag passiert.
"""
import json
import os
import signal
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "dev")
COLOR = os.environ.get("APP_COLOR", "gray")
POD = socket.gethostname()
PORT = int(os.environ.get("PORT", "8080"))

PAGE = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>device-app v{v}</title>
<style>body{{margin:0;height:100vh;display:grid;place-items:center;font-family:system-ui;
background:{bg};color:#fff}}h1{{font-size:5rem;margin:0}}p{{font-size:1.3rem;opacity:.85}}</style>
</head><body><div style="text-align:center"><h1>Version {v}</h1>
<p>Farbe: {c} &middot; Pod: {p}</p></div></body></html>"""

BG = {"blue": "#1d4ed8", "green": "#15803d"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # Keep-Alive, damit Geraete "verbunden" bleiben koennen

    def _send(self, status, body, ctype):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/version"):
            body = json.dumps({"version": VERSION, "color": COLOR, "pod": POD})
            self._send(200, body, "application/json")
        elif self.path.startswith("/healthz"):
            self._send(200, "ok", "text/plain")
        else:
            page = PAGE.format(v=VERSION, c=COLOR, p=POD, bg=BG.get(COLOR, "#555"))
            self._send(200, page, "text/html; charset=utf-8")

    def log_message(self, *args):
        pass  # ruhige Logs


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    print(f"device-app version={VERSION} color={COLOR} pod={POD} port={PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
