#!/usr/bin/env python3
"""JCoin's single-operator node. Prototype only; not for real funds."""
import base64
import hashlib
import json
import os
import sqlite3
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "node-data"
DB_PATH = DATA / "jcoin.sqlite3"
KEY_PATH = DATA / "master-validator.key"
LANDING = ROOT / "index.html"
DASHBOARD = ROOT / "dashboard.html"
HOST, PORT = "127.0.0.1", 8765
COIN_CAP = 84_000_000
INITIAL_REWARD = 50
HALVING_INTERVAL = 840_000
LOCK = threading.RLock()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def address_for(public_key):
    return "JC" + sha256(public_key)[:40]


def load_or_create_key():
    DATA.mkdir(mode=0o700, parents=True, exist_ok=True)
    if KEY_PATH.exists():
        return Ed25519PrivateKey.from_private_bytes(KEY_PATH.read_bytes())
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                            serialization.NoEncryption())
    fd = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    return key


MASTER_KEY = load_or_create_key()
MASTER_PUB = MASTER_KEY.public_key().public_bytes(
    serialization.Encoding.Raw, serialization.PublicFormat.Raw)
MASTER_ADDR = address_for(MASTER_PUB)
MASTER_PUB_B64 = base64.b64encode(MASTER_PUB).decode("ascii")
DATA.mkdir(mode=0o700, parents=True, exist_ok=True)
DB = sqlite3.connect(DB_PATH, check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.execute("PRAGMA journal_mode=WAL")
DB.execute("""CREATE TABLE IF NOT EXISTS blocks(
    height INTEGER PRIMARY KEY, body TEXT NOT NULL, block_hash TEXT NOT NULL,
    signature TEXT NOT NULL)""")
DB.execute("""CREATE TABLE IF NOT EXISTS pending(
    txid TEXT PRIMARY KEY, body TEXT NOT NULL)""")
DB.commit()


def signable_tx(tx):
    return {k: tx[k] for k in ("amount", "from", "nonce", "pub", "time", "to")}


def reward_at(height):
    halvings = height // HALVING_INTERVAL
    return 0 if halvings >= 63 else INITIAL_REWARD >> halvings


def all_blocks():
    return [json.loads(row["body"]) for row in DB.execute(
        "SELECT body FROM blocks ORDER BY height")]


def balances_and_nonces():
    balances, nonces, minted = {}, {}, 0
    for block in all_blocks():
        if block["reward"]:
            addr = block["validator"]
            balances[addr] = balances.get(addr, 0) + block["reward"]
            minted += block["reward"]
        for tx in block["transactions"]:
            balances[tx["from"]] = balances.get(tx["from"], 0) - tx["amount"]
            balances[tx["to"]] = balances.get(tx["to"], 0) + tx["amount"]
            nonces[tx["from"]] = tx["nonce"] + 1
    return balances, nonces, minted


def validate_tx(tx, balances, nonces, pending_spent):
    if not isinstance(tx, dict):
        raise ValueError("Transaction must be an object.")
    try:
        amount, nonce = tx["amount"], tx["nonce"]
        sender, recipient = tx["from"], tx["to"]
        pub = base64.b64decode(tx["pub"], validate=True)
        signature = base64.b64decode(tx["sig"], validate=True)
        stamp = tx["time"]
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("Transaction fields are missing or malformed.") from exc
    if type(amount) is not int or amount <= 0:
        raise ValueError("Amount must be a positive whole number of JCOIN.")
    if type(nonce) is not int or nonce < 0 or type(stamp) is not int:
        raise ValueError("Invalid transaction nonce or timestamp.")
    if abs(int(time.time()) - stamp) > 7 * 24 * 60 * 60:
        raise ValueError("Transaction timestamp is out of date.")
    if (not isinstance(sender, str) or not isinstance(recipient, str)
            or not sender.startswith("JC") or len(sender) != 42
            or not recipient.startswith("JC") or len(recipient) != 42
            or any(c not in "0123456789abcdef" for c in sender[2:] + recipient[2:])):
        raise ValueError("Addresses must use JC followed by 40 lowercase hexadecimal characters.")
    if address_for(pub) != sender:
        raise ValueError("Public key does not match the sender address.")
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(
            signature, canonical(signable_tx(tx)).encode("ascii"))
    except (InvalidSignature, ValueError) as exc:
        raise ValueError("Transaction signature is invalid.") from exc
    expected_nonce = nonces.get(sender, 0)
    already_pending = sum(1 for item in pending_spent if item["from"] == sender)
    if nonce != expected_nonce + already_pending:
        raise ValueError("Transaction nonce is out of date. Refresh and retry.")
    available = balances.get(sender, 0) - sum(
        item["amount"] for item in pending_spent if item["from"] == sender)
    if available < amount:
        raise ValueError("Not enough confirmed JCOIN for this transfer.")
    return True


def chain_status():
    blocks = all_blocks()
    balances, _, minted = balances_and_nonces()
    pending = DB.execute("SELECT COUNT(*) FROM pending").fetchone()[0]
    height = len(blocks) - 1
    return {
        "height": height, "blocks": len(blocks), "pending": pending,
        "master": MASTER_ADDR, "master_balance": balances.get(MASTER_ADDR, 0),
        "minted": minted, "cap": COIN_CAP,
        "next_reward": min(reward_at(height + 1), max(0, COIN_CAP - minted)),
        "validator": MASTER_ADDR, "validator_public_key": MASTER_PUB_B64,
        "network": "JCoin local prototype",
    }


def initialize_chain():
    if DB.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]:
        return
    body = {"height": 0, "time": int(time.time()), "previous": "0" * 64,
            "transactions": [], "reward": 0, "validator": MASTER_ADDR}
    block_hash = sha256(canonical(body).encode("ascii"))
    signature = base64.b64encode(MASTER_KEY.sign(bytes.fromhex(block_hash))).decode("ascii")
    DB.execute("INSERT INTO blocks VALUES(?,?,?,?)",
               (0, canonical(body), block_hash, signature))
    DB.commit()


def verify_chain():
    previous = "0" * 64
    rows = DB.execute("SELECT height,body,block_hash,signature FROM blocks ORDER BY height").fetchall()
    for height, row in enumerate(rows):
        block = json.loads(row["body"])
        if block["height"] != height or block["previous"] != previous:
            raise RuntimeError("JCoin chain link or height is invalid.")
        block_hash = sha256(canonical(block).encode("ascii"))
        if block_hash != row["block_hash"]:
            raise RuntimeError("Block data does not match its hash.")
        try:
            MASTER_KEY.public_key().verify(base64.b64decode(row["signature"]),
                                           bytes.fromhex(block_hash))
        except (InvalidSignature, ValueError) as exc:
            raise RuntimeError("Block validator signature is invalid.") from exc
        previous = block_hash


def get_account(address):
    balances, nonces, _ = balances_and_nonces()
    pending = [json.loads(r["body"]) for r in DB.execute(
        "SELECT body FROM pending ORDER BY rowid")]
    reserved = sum(t["amount"] for t in pending if t["from"] == address)
    incoming = sum(t["amount"] for t in pending if t["to"] == address)
    return {"address": address, "balance": balances.get(address, 0),
            "available": balances.get(address, 0) - reserved, "pending_in": incoming,
            "nonce": nonces.get(address, 0) + sum(1 for t in pending if t["from"] == address)}


def make_block():
    with LOCK:
        pending = [json.loads(r["body"]) for r in DB.execute(
            "SELECT body FROM pending ORDER BY rowid")]
        balances, nonces, minted = balances_and_nonces()
        accepted = []
        for tx in pending:
            try:
                validate_tx(tx, balances, nonces, accepted)
                accepted.append(tx)
            except ValueError:
                continue
        height = DB.execute("SELECT COALESCE(MAX(height),-1)+1 FROM blocks").fetchone()[0]
        reward = min(reward_at(height), max(0, COIN_CAP - minted))
        if reward <= 0 and not accepted:
            raise ValueError("Supply cap reached; no transfers are waiting.")
        previous = DB.execute(
            "SELECT block_hash FROM blocks ORDER BY height DESC LIMIT 1").fetchone()["block_hash"]
        block = {"height": height, "time": int(time.time()), "previous": previous,
                 "transactions": accepted, "reward": reward, "validator": MASTER_ADDR}
        block_hash = sha256(canonical(block).encode("ascii"))
        signature = base64.b64encode(MASTER_KEY.sign(bytes.fromhex(block_hash))).decode("ascii")
        DB.execute("INSERT INTO blocks VALUES(?,?,?,?)",
                   (height, canonical(block), block_hash, signature))
        DB.execute("DELETE FROM pending")
        DB.commit()
        return {"height": height, "hash": block_hash, "reward": reward,
                "confirmed": len(accepted)}


class Handler(BaseHTTPRequestHandler):
    server_version = "JCoinNode/0.1"

    def log_message(self, fmt, *args):
        safe_args = args
        if args and isinstance(args[0], str):
            request_parts = args[0].split()
            if len(request_parts) >= 2:
                # Query strings can contain wallet addresses; keep them out of
                # terminal output and scrollback.
                request_parts[1] = urlparse(request_parts[1]).path or "/"
                safe_args = (" ".join(request_parts),) + args[1:]
        print("%s - %s" % (self.address_string(), fmt % safe_args), flush=True)

    def local_operator(self):
        origin = self.headers.get("Origin")
        trusted_origins = (None, "http://127.0.0.1:8765", "http://localhost:8765")
        return (self.client_address[0] in ("127.0.0.1", "::1")
                and origin in trusted_origins)

    def send_json(self, code, value):
        data = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > 16_384:
            raise ValueError("Request is empty or too large.")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("Expected a JSON object.")
        return value

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        pages = {
            "/": LANDING,
            "/index.html": LANDING,
            "/dashboard": DASHBOARD,
            "/dashboard.html": DASHBOARD,
            "/JCoin-Wallet.html": ROOT / "JCoin-Wallet.html",
        }
        if parsed.path in pages:
            page = pages[parsed.path]
            data = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        elif parsed.path == "/api/status":
            self.send_json(200, chain_status())
        elif parsed.path == "/api/balance":
            address = parse_qs(parsed.query).get("address", [""])[0]
            self.send_json(200, get_account(address))
        elif parsed.path == "/api/blocks":
            rows = DB.execute(
                "SELECT body,block_hash,signature FROM blocks ORDER BY height DESC LIMIT 12"
            ).fetchall()
            result = []
            for row in reversed(rows):
                block = json.loads(row["body"])
                result.append({"height": block["height"], "time": block["time"],
                    "previous": block["previous"], "hash": row["block_hash"],
                    "signature": row["signature"], "validator": block["validator"],
                    "reward": block["reward"], "transactions": len(block["transactions"])})
            self.send_json(200, result)
        elif parsed.path == "/api/pending":
            if not self.local_operator():
                self.send_json(403, {"error": "Pending transaction details are local-only."})
                return
            rows = DB.execute("SELECT body FROM pending ORDER BY rowid").fetchall()
            self.send_json(200, [json.loads(r["body"]) for r in rows])
        else:
            self.send_json(404, {"error": "Not found."})

    def do_POST(self):
        try:
            body = self.read_json()
            if self.path == "/api/transaction":
                with LOCK:
                    balances, nonces, _ = balances_and_nonces()
                    pending = [json.loads(r["body"]) for r in DB.execute(
                        "SELECT body FROM pending ORDER BY rowid")]
                    validate_tx(body, balances, nonces, pending)
                    txid = sha256(canonical(body).encode("ascii"))
                    DB.execute("INSERT INTO pending VALUES(?,?)", (txid, canonical(body)))
                    DB.commit()
                self.send_json(201, {"txid": txid, "queued": True})
            elif self.path == "/api/master/send":
                if not self.local_operator():
                    self.send_json(403, {"error": "Master wallet actions are local-only."})
                    return
                target, amount = body.get("to", ""), body.get("amount")
                if isinstance(target, str) and len(target) == 42 and target[:2].upper() == "JC":
                    target = "JC" + target[2:].lower()
                if (type(amount) is not int or amount <= 0 or not isinstance(target, str)
                        or len(target) != 42 or not target.startswith("JC")
                        or any(c not in "0123456789abcdef" for c in target[2:])):
                    raise ValueError("Enter a valid destination and whole coin amount.")
                account = get_account(MASTER_ADDR)
                tx = {"amount": amount, "from": MASTER_ADDR, "nonce": account["nonce"],
                      "pub": MASTER_PUB_B64, "time": int(time.time()), "to": target}
                tx["sig"] = base64.b64encode(
                    MASTER_KEY.sign(canonical(signable_tx(tx)).encode("ascii"))).decode("ascii")
                balances, nonces, _ = balances_and_nonces()
                pending = [json.loads(r["body"]) for r in DB.execute(
                    "SELECT body FROM pending ORDER BY rowid")]
                validate_tx(tx, balances, nonces, pending)
                txid = sha256(canonical(tx).encode("ascii"))
                DB.execute("INSERT INTO pending VALUES(?,?)", (txid, canonical(tx)))
                DB.commit()
                self.send_json(201, {"txid": txid, "queued": True})
            elif self.path == "/api/validate":
                if not self.local_operator():
                    self.send_json(403, {"error": "Only the laptop operator can validate blocks."})
                    return
                self.send_json(200, make_block())
            else:
                self.send_json(404, {"error": "Not found."})
        except sqlite3.IntegrityError:
            self.send_json(409, {"error": "That transfer is already queued."})
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {"error": "Node error: " + str(exc)})


def main():
    missing_pages = [str(page.name) for page in (LANDING, DASHBOARD) if not page.exists()]
    if missing_pages:
        raise SystemExit("Required web page(s) missing beside jcoin_node.py: " + ", ".join(missing_pages))
    initialize_chain()
    verify_chain()
    print("JCoin node and validator started.")
    print("Master wallet: " + MASTER_ADDR)
    print("Master key: " + str(KEY_PATH) + " (keep it private and back it up)")
    print("Jcoin home: http://127.0.0.1:%d" % PORT)
    print("Local dashboard: http://127.0.0.1:%d/dashboard" % PORT)
    print("Local-only mode: other computers cannot connect in this prototype.")
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:%d" % PORT)).start()
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except OSError as exc:
        raise SystemExit("Could not start JCoin node: " + str(exc))


if __name__ == "__main__":
    main()
