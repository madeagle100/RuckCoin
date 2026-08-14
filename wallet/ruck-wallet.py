#!/usr/bin/env python3
"""RuckCoin local wallet. Binds to 127.0.0.1 only. Talks to your node."""
from __future__ import annotations

import base64
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HOST = "127.0.0.1"
PORT = 8870
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

if os.name == "nt":
    CFG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "Ruck"
else:
    CFG_DIR = Path.home() / ".ruck"
CFG_PATH = CFG_DIR / "wallet-ui.json"

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 8866,
    "user": "ruck",
    "password": "",
    "receive_address": "",
    "veterans_address": "",
}


def load_cfg() -> dict:
    data = dict(DEFAULTS)
    if CFG_PATH.exists():
        try:
            raw = CFG_PATH.read_text(encoding="utf-8-sig")
            data.update(json.loads(raw))
        except (OSError, json.JSONDecodeError):
            pass
    return data


def save_cfg(data: dict) -> None:
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    CFG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


_cfg_lock = threading.Lock()
_cfg = load_cfg()


def rpc(method: str, params=None, timeout: int = 30):
    with _cfg_lock:
        cfg = dict(_cfg)
    url = f"http://{cfg['host']}:{int(cfg['port'])}/"
    payload = json.dumps(
        {"jsonrpc": "1.0", "id": "wallet", "method": method, "params": params or []}
    ).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    user, password = cfg.get("user") or "", cfg.get("password") or ""
    if user or password:
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(
                "The node refused the request. Check the port, user, and password in Settings."
            ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Cannot reach the RuckCoin node. Start the node first, then try again."
        ) from e
    if body.get("error"):
        err = body["error"]
        if isinstance(err, dict):
            raise RuntimeError(err.get("message") or str(err))
        raise RuntimeError(str(err))
    return body.get("result")


def json_out(handler: BaseHTTPRequestHandler, code: int, obj) -> None:
    data = json.dumps(obj).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.write_body(data)


def file_out(handler: BaseHTTPRequestHandler, path: Path, ctype: str) -> None:
    data = path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.write_body(data)


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode() or "{}")


def overview() -> dict:
    chain = rpc("getblockchaininfo")
    wallet = rpc("getwalletinfo")
    try:
        mining = rpc("getmininginfo")
    except Exception:
        mining = {}
    try:
        net = rpc("getnetworkinfo")
    except Exception:
        net = {}
    try:
        assets = rpc("listmyassets")
    except Exception:
        assets = {}
    try:
        txs = rpc("listtransactions", ["*", 20, 0])
    except Exception:
        txs = []
    with _cfg_lock:
        addr = _cfg.get("receive_address") or ""
        veterans = _cfg.get("veterans_address") or ""
    if not addr:
        best_amt = -1.0
        try:
            for group in rpc("listaddressgroupings") or []:
                for row in group:
                    if not row:
                        continue
                    cand = row[0]
                    amt = float(row[1]) if len(row) > 1 else 0.0
                    if cand and amt > best_amt:
                        best_amt = amt
                        addr = cand
        except Exception:
            addr = ""
        if not addr:
            try:
                got = rpc("listreceivedbyaddress", [0, True, True]) or []
                if got:
                    addr = got[0].get("address") or ""
            except Exception:
                addr = ""
        if not addr:
            addr = rpc("getnewaddress", ["My address"])
        with _cfg_lock:
            _cfg["receive_address"] = addr
            save_cfg(_cfg)
    return {
        "ok": True,
        "height": chain.get("blocks"),
        "tip": chain.get("bestblockhash"),
        "chain": chain.get("chain"),
        "balance": wallet.get("balance", 0),
        "unconfirmed": wallet.get("unconfirmed_balance", 0),
        "immature": wallet.get("immature_balance", 0),
        "txcount": wallet.get("txcount", 0),
        "address": addr,
        "veterans_address": veterans,
        "assets": assets if isinstance(assets, dict) else {},
        "txs": txs if isinstance(txs, list) else [],
        "mining": {
            "blocks": mining.get("blocks"),
            "difficulty": mining.get("difficulty"),
            "networkhashps": mining.get("networkhashps"),
            "pooledtx": mining.get("pooledtx"),
        },
        "network": {
            "active": bool(net.get("networkactive", True)),
            "connections": int(net.get("connections") or 0),
        },
    }


class Handler(BaseHTTPRequestHandler):
    def write_body(self, data: bytes) -> None:
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in ("/", "/index.html"):
            return file_out(self, STATIC / "index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            name = path[len("/static/") :]
            if ".." in name or name.startswith("/"):
                self.send_error(404)
                return
            fp = STATIC / name
            if not fp.is_file():
                self.send_error(404)
                return
            ctype = {
                ".css": "text/css; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".svg": "image/svg+xml",
                ".png": "image/png",
                ".jpg": "image/jpeg",
            }.get(fp.suffix, "application/octet-stream")
            return file_out(self, fp, ctype)
        if path == "/api/overview":
            try:
                return json_out(self, 200, overview())
            except Exception as e:
                return json_out(self, 503, {"ok": False, "error": str(e)})
        if path == "/api/settings":
            with _cfg_lock:
                public = {
                    "host": _cfg.get("host"),
                    "port": _cfg.get("port"),
                    "user": _cfg.get("user"),
                    "has_password": bool(_cfg.get("password")),
                    "veterans_address": _cfg.get("veterans_address") or "",
                }
            return json_out(self, 200, {"ok": True, **public})
        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = read_json(self)
        except json.JSONDecodeError:
            return json_out(self, 400, {"ok": False, "error": "That request was not valid."})
        try:
            if path == "/api/connect":
                nxt = {
                    "host": (body.get("host") or "127.0.0.1").strip(),
                    "port": int(body.get("port") or 8866),
                    "user": (body.get("user") or "").strip(),
                    "password": body.get("password"),
                    "veterans_address": (body.get("veterans_address") or "").strip(),
                }
                with _cfg_lock:
                    if nxt["password"] is None or nxt["password"] == "":
                        nxt["password"] = _cfg.get("password") or ""
                    _cfg.update(nxt)
                    save_cfg(_cfg)
                info = rpc("getblockchaininfo")
                return json_out(
                    self,
                    200,
                    {"ok": True, "height": info.get("blocks"), "message": "Connected to your node."},
                )
            if path == "/api/new-address":
                label = (body.get("label") or "My address").strip() or "My address"
                addr = rpc("getnewaddress", [label])
                with _cfg_lock:
                    _cfg["receive_address"] = addr
                    save_cfg(_cfg)
                return json_out(self, 200, {"ok": True, "address": addr})
            if path == "/api/send":
                dest = (body.get("to") or "").strip()
                amount = float(body.get("amount") or 0)
                donate = bool(body.get("donate"))
                donate_amt = float(body.get("donate_amount") or 0)
                if not dest.startswith("K") and not dest.startswith("k"):
                    return json_out(
                        self,
                        400,
                        {
                            "ok": False,
                            "error": "That does not look like a RuckCoin address. RuckCoin addresses start with K.",
                        },
                    )
                if amount <= 0:
                    return json_out(self, 400, {"ok": False, "error": "Enter an amount greater than zero."})
                with _cfg_lock:
                    vets = (_cfg.get("veterans_address") or "").strip()
                if donate:
                    if not vets:
                        return json_out(
                            self,
                            400,
                            {
                                "ok": False,
                                "error": "No veterans address is set yet. Leave the donation off, or add the official address in Settings after launch.",
                            },
                        )
                    if donate_amt <= 0:
                        return json_out(
                            self,
                            400,
                            {"ok": False, "error": "Turn donation off, or enter a donation amount."},
                        )
                    txid = rpc("sendmany", ["", {dest: amount, vets: donate_amt}])
                else:
                    txid = rpc("sendtoaddress", [dest, amount])
                return json_out(self, 200, {"ok": True, "txid": txid})
            if path == "/api/transfer":
                name = (body.get("asset") or "").strip()
                dest = (body.get("to") or "").strip()
                qty = float(body.get("qty") or 0)
                if not name or qty <= 0 or not dest:
                    return json_out(
                        self,
                        400,
                        {"ok": False, "error": "Need an asset name, an amount, and a K address."},
                    )
                txid = rpc("transfer", [name, qty, dest])
                return json_out(self, 200, {"ok": True, "txid": txid})
            if path == "/api/offline":
                want_offline = bool(body.get("offline"))
                # false = stay off the public network; true = allow peers
                active = rpc("setnetworkactive", [not want_offline])
                return json_out(
                    self,
                    200,
                    {
                        "ok": True,
                        "offline": not bool(active),
                        "message": (
                            "This computer will not talk to other RuckCoin computers until you turn the internet back on."
                            if want_offline
                            else "This computer may talk to other RuckCoin computers again."
                        ),
                    },
                )
            if path == "/api/mine":
                with _cfg_lock:
                    addr = _cfg.get("receive_address") or ""
                if not addr:
                    addr = rpc("getnewaddress", ["Miner"])
                    with _cfg_lock:
                        _cfg["receive_address"] = addr
                        save_cfg(_cfg)
                tries = int(body.get("tries") or 200000)
                tries = max(1000, min(tries, 500000))
                # generatetoaddress nblocks address maxtries
                hashes = rpc("generatetoaddress", [1, addr, tries], timeout=120)
                found = bool(hashes)
                return json_out(
                    self,
                    200,
                    {
                        "ok": True,
                        "found": found,
                        "blocks": hashes or [],
                        "address": addr,
                        "tries": tries,
                    },
                )
        except Exception as e:
            return json_out(self, 400, {"ok": False, "error": str(e)})
        self.send_error(404)


def main():
    if not (STATIC / "index.html").is_file():
        print("Missing wallet/static/index.html", file=sys.stderr)
        sys.exit(1)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"RuckCoin wallet  http://{HOST}:{PORT}")
    print("This window must stay open while you use the wallet.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
