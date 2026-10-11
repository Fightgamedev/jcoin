#!/usr/bin/env python3
"""Jcoin CodeQ: deterministic, conservation-preserving payment intent compiler.

CodeQ is a declarative prototype. It never executes user-provided code and does
not submit or sign transactions.
"""
import hashlib
import json
import re
import time
from typing import Any


VERSION = "jcoin-codeq/0.1"
BASIS_POINTS = 10_000
MAX_LANES = 16
ADDRESS_RE = re.compile(r"^JC[0-9a-f]{40}$")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _require_int(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer greater than or equal to {minimum}.")
    return value


def compile_codeq(intent: dict[str, Any], now: int | None = None) -> dict[str, Any]:
    """Compile a Q-intent into deterministic whole-JCOIN output allocations.

    Each lane's weight is expressed in basis points and all lane weights must
    sum to 10,000. Integer division produces initial shares; remaining units
    go to lanes with the largest fractional remainders. Ties are broken by a
    hash of the intent ID and lane ID, so every implementation gets the same
    result without a validator choosing who receives rounding units.
    """
    if not isinstance(intent, dict):
        raise ValueError("CodeQ intent must be an object.")

    intent_id = intent.get("id")
    if not isinstance(intent_id, str) or not intent_id.strip() or len(intent_id) > 96:
        raise ValueError("Intent id must contain 1 to 96 characters.")

    amount = _require_int(intent.get("amount"), "Amount", 1)
    expires_at = _require_int(intent.get("expires_at"), "Expiry", 1)
    current_time = int(time.time()) if now is None else _require_int(now, "Current time")
    if expires_at <= current_time:
        raise ValueError("CodeQ intent has expired.")

    memo = intent.get("memo", "")
    if not isinstance(memo, str) or len(memo) > 140:
        raise ValueError("Memo must be text of at most 140 characters.")

    lanes = intent.get("lanes")
    if not isinstance(lanes, list) or not 1 <= len(lanes) <= MAX_LANES:
        raise ValueError(f"CodeQ intent must contain 1 to {MAX_LANES} payment lanes.")

    normalized = []
    lane_ids = set()
    destinations = set()
    for lane in lanes:
        if not isinstance(lane, dict):
            raise ValueError("Each payment lane must be an object.")
        lane_id = lane.get("id")
        recipient = lane.get("to")
        weight = _require_int(lane.get("weight_bps"), "Lane weight", 1)
        if not isinstance(lane_id, str) or not lane_id.strip() or len(lane_id) > 48:
            raise ValueError("Lane id must contain 1 to 48 characters.")
        if not isinstance(recipient, str) or not ADDRESS_RE.fullmatch(recipient):
            raise ValueError("Lane recipient must be a lowercase Jcoin address.")
        if lane_id in lane_ids:
            raise ValueError("Lane ids must be unique.")
        if recipient in destinations:
            raise ValueError("Each CodeQ lane must have a unique recipient.")
        lane_ids.add(lane_id)
        destinations.add(recipient)
        normalized.append({"id": lane_id, "to": recipient, "weight_bps": weight})

    if sum(lane["weight_bps"] for lane in normalized) != BASIS_POINTS:
        raise ValueError("Lane weights must add up to exactly 10,000 basis points.")

    shares = []
    for lane in normalized:
        numerator = amount * lane["weight_bps"]
        base, remainder = divmod(numerator, BASIS_POINTS)
        tie_key = hashlib.sha256(
            (intent_id + "\0" + lane["id"] + "\0" + lane["to"]).encode("utf-8")
        ).digest()
        shares.append({**lane, "amount": base, "remainder": remainder, "tie_key": tie_key})

    undistributed = amount - sum(share["amount"] for share in shares)
    ranked = sorted(shares, key=lambda share: (-share["remainder"], share["tie_key"]))
    for share in ranked[:undistributed]:
        share["amount"] += 1

    allocations = [
        {"id": share["id"], "to": share["to"], "weight_bps": share["weight_bps"],
         "amount": share["amount"]}
        for share in sorted(shares, key=lambda share: share["id"])
    ]
    clean_intent = {
        "version": VERSION,
        "id": intent_id,
        "amount": amount,
        "expires_at": expires_at,
        "memo": memo,
        "lanes": sorted(normalized, key=lambda lane: lane["id"]),
    }
    committed = {"intent": clean_intent, "allocations": allocations}
    return {
        **committed,
        "quantum": "1 JCOIN",
        "conservation": {
            "input": amount,
            "allocated": sum(item["amount"] for item in allocations),
        },
        "commitment": hashlib.sha256(canonical(committed).encode("ascii")).hexdigest(),
    }


def verify_codeq(compiled: dict[str, Any], now: int | None = None) -> bool:
    """Recompile and compare a CodeQ object; reject edited or noncanonical output."""
    if not isinstance(compiled, dict) or not isinstance(compiled.get("intent"), dict):
        return False
    intent = dict(compiled["intent"])
    if intent.pop("version", None) != VERSION:
        return False
    try:
        expected = compile_codeq(intent, now=now)
    except (TypeError, ValueError):
        return False
    return canonical(expected) == canonical(compiled)


def demo() -> None:
    """Print a small example of one payment split across three destinations."""
    intent = {
        "id": "demo-cafe-001",
        "amount": 101,
        "expires_at": int(time.time()) + 3600,
        "memo": "Example only; no payment is sent.",
        "lanes": [
            {"id": "merchant", "to": "JC" + "1" * 40, "weight_bps": 9000},
            {"id": "roundup", "to": "JC" + "2" * 40, "weight_bps": 700},
            {"id": "community", "to": "JC" + "3" * 40, "weight_bps": 300},
        ],
    }
    print(json.dumps(compile_codeq(intent), indent=2))


if __name__ == "__main__":
    demo()
