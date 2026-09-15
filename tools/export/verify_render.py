#!/usr/bin/env python3
"""
OBSOLETE — remplace par tools/export/verify_final.js. NE PAS UTILISER.

Pourquoi ce script ne fonctionne plus :
  Le serveur MCP Playwright du conteneur lance le canal navigateur 'chrome',
  absent de l'image (seul 'chromium' est installe). L'appel echoue sur :
      Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome

Contournement retenu : verifier le rendu en pilotant playwright-core
directement, sans passer par le serveur MCP.
  -> voir tools/export/verify_final.js et docs/viewer-3d.md
  -> ou relancer 4 fois `npx playwright install chrome` en connaissance de cause

Ce fichier est conserve comme trace du diagnostic, pas comme outil.

Sequence d'origine (pour memoire) :
  1. initialize + notifications/initialized
  2. tools/list  -> verifier que navigate n'est pas deja occupe
  3. browser_navigate vers la page servie
  4. browser_evaluate : lire window.__CHECKS (verdict du viewer)
  5. browser_evaluate : compter les objets reellement rendus (canvas + WebGL)
  6. browser_take_screenshot -> PNG
"""
import json, urllib.request, sys, time

MCP = "http://172.16.1.10:3334/mcp"
PAGE = "http://172.16.1.1:8931/index.html"
HEADERS = {"Content-Type": "application/json",
           "Accept": "application/json, text/event-stream"}

_id = [0]
_session = [None]


def rpc(method, params=None, notify=False):
    _id[0] += 1
    body = {"jsonrpc": "2.0", "method": method}
    if not notify:
        body["id"] = _id[0]
    if params is not None:
        body["params"] = params
    headers = dict(HEADERS)
    if _session[0]:
        headers["mcp-session-id"] = _session[0]
    req = urllib.request.Request(MCP, data=json.dumps(body).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        sid = r.headers.get("mcp-session-id")
        if sid:
            _session[0] = sid
        raw = r.read().decode()
    # le serveur MCP repond en SSE : on extrait la ligne data:
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:].strip()
            break
    if not raw.strip():
        return None
    return json.loads(raw)


def rpc_retry(method, params=None, tries=2):
    last = None
    for i in range(tries):
        try:
            return rpc(method, params)
        except Exception as e:
            last = e
            time.sleep(1.5)
    raise last


def call_tool(name, args, tries=2):
    last = None
    for i in range(tries):
        try:
            r = rpc("tools/call", {"name": name, "arguments": args})
            if r and "result" in r:
                out = r["result"].get("content") or []
                texts = [c.get("text", "") for c in out if c.get("type") == "text"]
                return "\n".join(texts)
            return json.dumps(r)
        except Exception as e:
            last = e
            time.sleep(1.5)
    raise last


def main():
    print("=== 1. initialize ===")
    r = rpc("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "swarm-verif", "version": "1.0"},
    })
    srv = (r or {}).get("result", {}).get("serverInfo", {})
    print("   serveur :", srv)
    rpc("notifications/initialized", notify=True)

    print("=== 2. tools/list ===")
    r = rpc("tools/list")
    tools = [t["name"] for t in (r or {}).get("result", {}).get("tools", [])]
    print("   outils :", ", ".join(tools[:14]), "..." if len(tools) > 14 else "")

    print(f"=== 3. navigate -> {PAGE} ===")
    try:
        print("   ", call_tool("browser_navigate", {"url": PAGE})[:600])
    except Exception as e:
        print("   ECHEC navigation :", e)
        return 2

    time.sleep(4)  # laisser charger three.js depuis le CDN + construire la scene

    print("=== 4. verdict du viewer (window.__CHECKS) ===")
    try:
        v = call_tool("browser_evaluate", {
            "function": "() => JSON.stringify(window.__CHECKS || {error:'__CHECKS absent'})"})
        print("   ", v[:900])
    except Exception as e:
        print("   ECHEC evaluate :", e)

    print("=== 5. l'objet etait-il bien servi (non vide) ? ===")
    try:
        v = call_tool("browser_evaluate", {
            "function": "() => JSON.stringify({title: document.title, banner: (document.getElementById('banner')||{}).innerText, hasThree: typeof window.THREE !== 'undefined', canvas: (()=>{const c=document.querySelector('canvas'); if(!c) return null; return {w:c.width,h:c.height};})()})"})
        print("   ", v[:900])
    except Exception as e:
        print("   ECHEC evaluate :", e)

    print("=== 6. screenshot ===")
    try:
        print("   ", call_tool("browser_take_screenshot", {
            "filename": "viewer-render.png", "type": "png"})[:500])
    except Exception as e:
        print("   ECHEC screenshot :", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
