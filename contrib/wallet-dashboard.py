#!/usr/bin/env python3
"""Tiny local RuckCoin wallet view. Open http://127.0.0.1:8870"""
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

RPC_URL = "http://127.0.0.1:8866/"
RPC_AUTH = ("ruck", "ruckdev")


def rpc(method, params=None):
    payload = json.dumps(
        {"jsonrpc": "1.0", "id": "dash", "method": method, "params": params or []}
    ).encode()
    req = urllib.request.Request(RPC_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    import base64

    token = base64.b64encode(f"{RPC_AUTH[0]}:{RPC_AUTH[1]}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode())
    if body.get("error"):
        raise RuntimeError(body["error"])
    return body["result"]


HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>RuckCoin</title>
<style>
body{font-family:Segoe UI,sans-serif;background:#0f1720;color:#e8eef5;margin:40px}
h1{margin:0 0 8px;font-size:28px}
.sub{color:#9bb0c3;margin-bottom:24px}
.card{background:#182230;border-radius:12px;padding:20px 24px;margin:12px 0;max-width:640px}
.k{color:#9bb0c3;font-size:13px}
.v{font-size:26px;font-weight:600;margin-top:4px}
code{color:#7dd3a0}
</style></head><body>
<h1>RuckCoin test wallet</h1>
<p class="sub">Local node &mdash; not Ravencoin. This page is the working view while the Linux Qt window is hidden.</p>
<div class="card"><div class="k">Height</div><div class="v">__HEIGHT__</div></div>
<div class="card"><div class="k">Spendable RUCK</div><div class="v">__BALANCE__</div></div>
<div class="card"><div class="k">Immature RUCK</div><div class="v">__IMMATURE__</div></div>
<div class="card"><div class="k">Assets</div><div class="v"><code>__ASSETS__</code></div></div>
<div class="card"><div class="k">Tip</div><div class="v" style="font-size:14px"><code>__TIP__</code></div></div>
<p class="sub">Refresh this page to update. Miner address: <code>KEPRbPbSLRbS3r6VaaXxH1MizfB9b97cc7</code></p>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            chain = rpc("getblockchaininfo")
            wallet = rpc("getwalletinfo")
            try:
                assets = rpc("listmyassets")
            except Exception:
                assets = {}
            page = (
                HTML.replace("__HEIGHT__", str(chain.get("blocks")))
                .replace("__BALANCE__", f"{wallet.get('balance', 0):,.8f}")
                .replace("__IMMATURE__", f"{wallet.get('immature_balance', 0):,.8f}")
                .replace("__ASSETS__", json.dumps(assets))
                .replace("__TIP__", chain.get("bestblockhash", ""))
            )
            data = page.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            msg = f"<pre>Node error: {e}\nIs ruckd running?</pre>".encode()
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    print("Open http://127.0.0.1:8870")
    HTTPServer(("127.0.0.1", 8870), Handler).serve_forever()
