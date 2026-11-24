"""Geraete-Simulator mit Live-Dashboard.

Jedes simulierte Geraet haelt eine Keep-Alive-Verbindung zur App (wie ein real
angeschlossenes Geraet) und fragt regelmaessig /api/version ab. Nach SESSION_SECONDS
baut es die Verbindung neu auf - dabei verteilt der Kubernetes-Service neu, und
so wandern Geraete Stueck fuer Stueck auf die neue Version, sobald es Pods davon gibt.
Wird ein Pod beendet, verbinden sich seine Geraete sofort neu.

Konfiguration ueber Umgebungsvariablen:
  TARGET_URL       z.B. http://device-app.env-rollouts.svc:80
  DEVICES          Anzahl Geraete (Standard 20)
  INTERVAL         Sekunden zwischen Abfragen (Standard 1)
  SESSION_SECONDS  Verbindungsdauer bis Neuverbindung (Standard 10, 0 = jede Anfrage neu)
  ENV_NAME         Anzeigename der Umgebung
  STRATEGY         Anzeigetext der Strategie
"""
import http.client
import json
import os
import random
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

TARGET = urlparse(os.environ.get("TARGET_URL", "http://device-app:80"))
DEVICES = int(os.environ.get("DEVICES", "20"))
INTERVAL = float(os.environ.get("INTERVAL", "1"))
SESSION_SECONDS = float(os.environ.get("SESSION_SECONDS", "10"))
ENV_NAME = os.environ.get("ENV_NAME", "unbekannt")
STRATEGY = os.environ.get("STRATEGY", "")
PORT = int(os.environ.get("PORT", "8080"))

lock = threading.Lock()
state = {}               # device_id -> letzter Status
events = deque(maxlen=40)  # Versionswechsel-Log


def device_loop(dev_id):
    conn = None
    session_start = 0.0
    time.sleep(random.uniform(0, INTERVAL))  # Start entzerren
    while True:
        result = None
        for attempt in range(2):  # bei Abbruch (Pod beendet) einmal sofort neu verbinden
            try:
                now = time.time()
                if conn is None or (SESSION_SECONDS == 0) or now - session_start > SESSION_SECONDS:
                    if conn:
                        conn.close()
                    conn = http.client.HTTPConnection(TARGET.hostname, TARGET.port or 80, timeout=3)
                    session_start = now
                conn.request("GET", "/api/version", headers={"X-Device-ID": dev_id})
                resp = conn.getresponse()
                body = resp.read()
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                result = json.loads(body)
                break
            except Exception as exc:  # noqa: BLE001
                if conn:
                    conn.close()
                conn = None
                result = {"error": str(exc)[:80]}
        with lock:
            prev = state.get(dev_id, {})
            entry = {"id": dev_id, "ts": time.time(), **result}
            if "error" not in result and prev.get("version") and prev.get("version") != result["version"]:
                events.appendleft({"ts": time.time(), "id": dev_id,
                                   "from": prev["version"], "to": result["version"]})
            if "error" in result:
                entry.setdefault("version", prev.get("version"))
                entry.setdefault("color", prev.get("color"))
            state[dev_id] = entry
        time.sleep(INTERVAL)


DASHBOARD = r"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>Geraete - __ENV__</title>
<style>
:root{--blue:#2563eb;--green:#16a34a;--gray:#6b7280;--bg:#0f172a;--card:#1e293b;--fg:#e2e8f0}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--fg);padding:24px}
h1{margin:0 0 4px;font-size:1.6rem}.sub{opacity:.7;margin-bottom:20px}
.bar{display:flex;height:34px;border-radius:8px;overflow:hidden;margin-bottom:8px;background:var(--card)}
.bar div{display:flex;align-items:center;justify-content:center;font-weight:600;transition:width .6s}
.legend{opacity:.8;margin-bottom:20px;font-size:.95rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px}
.dev{border-radius:10px;padding:10px;background:var(--card);border:3px solid var(--gray);transition:border-color .4s,background .4s}
.dev b{display:block;font-size:1.05rem}.dev small{opacity:.75;font-size:.72rem;word-break:break-all}
.dev.blue{border-color:var(--blue);background:#1e3a8a55}.dev.green{border-color:var(--green);background:#14532d66}
.dev.err{border-style:dashed}
.cols{display:grid;grid-template-columns:2fr 1fr;gap:24px;margin-top:24px}
.card{background:var(--card);border-radius:10px;padding:14px}.card h3{margin:0 0 8px;font-size:1rem}
ul{list-style:none;margin:0;padding:0;font-size:.85rem;max-height:260px;overflow:auto}li{padding:2px 0}
</style></head><body>
<h1>Geraete-Dashboard: __ENV__</h1><div class="sub">__STRATEGY__ &middot; <span id="n"></span> Geraete</div>
<div class="bar" id="bar"></div><div class="legend" id="legend"></div>
<div class="grid" id="grid"></div>
<div class="cols"><div class="card"><h3>Pods, die gerade antworten</h3><ul id="pods"></ul></div>
<div class="card"><h3>Versionswechsel (neueste oben)</h3><ul id="events"></ul></div></div>
<script>
const colorOf = c => c==='blue'?'var(--blue)':c==='green'?'var(--green)':'var(--gray)';
async function tick(){
  try{
    const d = await (await fetch('api/devices')).json();
    const devs = d.devices; document.getElementById('n').textContent = devs.length;
    const counts = {};
    devs.forEach(x=>{const k=x.version?('v'+x.version):'offline'; counts[k]=counts[k]||{n:0,color:x.color}; counts[k].n++;});
    const keys = Object.keys(counts).sort();
    document.getElementById('bar').innerHTML = keys.map(k=>{const p=100*counts[k].n/devs.length;
      return `<div style="width:${p}%;background:${colorOf(counts[k].color)}">${p>=8?k+' '+Math.round(p)+'%':''}</div>`}).join('');
    document.getElementById('legend').textContent = keys.map(k=>`${k}: ${counts[k].n} Geraete`).join('   |   ');
    document.getElementById('grid').innerHTML = devs.map(x=>`<div class="dev ${x.color||''} ${x.error?'err':''}">
      <b>${x.id}</b>${x.version?'v'+x.version:'-'}<br><small>${x.error?('Fehler: '+x.error):(x.pod||'')}</small></div>`).join('');
    const pods = {}; devs.forEach(x=>{if(x.pod&&!x.error){pods[x.pod]=pods[x.pod]||{n:0,v:x.version,c:x.color};pods[x.pod].n++;}});
    document.getElementById('pods').innerHTML = Object.entries(pods).sort().map(([p,i])=>
      `<li><span style="color:${colorOf(i.c)}">&#9679;</span> ${p} &middot; v${i.v} &middot; ${i.n} Geraet(e)</li>`).join('');
    document.getElementById('events').innerHTML = d.events.map(e=>
      `<li>${new Date(e.ts*1000).toLocaleTimeString()} &middot; ${e.id}: v${e.from} &rarr; v${e.to}</li>`).join('');
  }catch(e){}
}
setInterval(tick,1000); tick();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, ctype):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/devices"):
            with lock:
                devs = [state[k] for k in sorted(state)]
                body = json.dumps({"devices": devs, "events": list(events)})
            self._send(200, body, "application/json")
        elif self.path.startswith("/healthz"):
            self._send(200, "ok", "text/plain")
        else:
            page = DASHBOARD.replace("__ENV__", ENV_NAME).replace("__STRATEGY__", STRATEGY)
            self._send(200, page, "text/html; charset=utf-8")

    def log_message(self, *args):
        pass


def main():
    for i in range(1, DEVICES + 1):
        threading.Thread(target=device_loop, args=(f"geraet-{i:02d}",), daemon=True).start()
    print(f"simulator: {DEVICES} Geraete -> {TARGET.geturl()} (session {SESSION_SECONDS}s)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
