"""Ledger regression tests use an isolated disposable data directory."""
import base64
import json
import os
import shutil
import stat
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


_test_data = tempfile.TemporaryDirectory(prefix="jcoin-ledger-tests-")
_old_data_dir = os.environ.get("JCOIN_DATA_DIR")
os.environ["JCOIN_DATA_DIR"] = _test_data.name
import jcoin_node as node  # noqa: E402  (the path must be set before node import)
if _old_data_dir is None:
    os.environ.pop("JCOIN_DATA_DIR", None)
else:
    os.environ["JCOIN_DATA_DIR"] = _old_data_dir


def make_key():
    return Ed25519PrivateKey.generate()


def make_tx(key, amount, nonce, recipient, stamp=None):
    public_key = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    tx = {
        "amount": amount,
        "from": node.address_for(public_key),
        "nonce": nonce,
        "pub": base64.b64encode(public_key).decode("ascii"),
        "time": int(time.time()) if stamp is None else stamp,
        "to": recipient,
    }
    tx["sig"] = base64.b64encode(
        key.sign(node.canonical(node.signable_tx(tx)).encode("ascii"))).decode("ascii")
    return tx


class NodeLedgerTests(unittest.TestCase):
    def setUp(self):
        with node.LOCK, node.DB:
            for table in ("blocks", "pending", "rejected", "faucet_claims"):
                node.DB.execute(f"DELETE FROM {table}")
        node.initialize_chain()

    def fund(self, key, amount=10):
        node.make_block()  # local validator earns its first prototype reward
        address = node.address_for(key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw))
        with node.LOCK, node.DB:
            node.queue_master_transfer(address, amount)
        node.make_block()
        return address

    def test_valid_signed_transfer_updates_balances_and_survives_chain_check(self):
        sender_key = make_key()
        sender = self.fund(sender_key)
        recipient = "JC" + "a" * 40
        tx = make_tx(sender_key, 7, 0, recipient)
        txid = node.sha256(node.canonical(tx).encode("ascii"))
        with node.LOCK, node.DB:
            node.DB.execute("INSERT INTO pending VALUES(?,?)", (txid, node.canonical(tx)))

        result = node.make_block()

        self.assertEqual(result["confirmed"], 1)
        self.assertEqual(node.get_account(sender)["balance"], 3)
        self.assertEqual(node.get_account(recipient)["balance"], 7)
        self.assertEqual(node.get_account(sender)["nonce"], 1)
        node.verify_chain()

    def test_unsigned_extra_transaction_fields_are_rejected(self):
        sender_key = make_key()
        sender = self.fund(sender_key)
        tx = make_tx(sender_key, 1, 0, "JC" + "b" * 40)
        tx["memo"] = "not covered by the signature"
        balances, nonces, _ = node.balances_and_nonces()
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            node.validate_tx(tx, balances, nonces, [])
        self.assertEqual(node.get_account(sender)["balance"], 10)

    def test_modified_signed_amount_is_rejected(self):
        sender_key = make_key()
        self.fund(sender_key)
        tx = make_tx(sender_key, 1, 0, "JC" + "f" * 40)
        tx["amount"] = 2
        balances, nonces, _ = node.balances_and_nonces()
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            node.validate_tx(tx, balances, nonces, [])

    def test_same_nonce_cannot_reserve_funds_twice(self):
        key = make_key()
        sender = self.fund(key)
        balances, nonces, _ = node.balances_and_nonces()
        first = make_tx(key, 8, 0, "JC" + "c" * 40)
        second = make_tx(key, 8, 0, "JC" + "d" * 40)
        node.validate_tx(first, balances, nonces, [])
        with self.assertRaisesRegex(ValueError, "nonce"):
            node.validate_tx(second, balances, nonces, [first])
        self.assertEqual(node.get_account(sender)["available"], 10)

    def test_faucet_claim_is_canonical_and_one_time(self):
        recipient_key = make_key()
        recipient = self.fund(recipient_key, amount=1)
        # The local faucet needs 100 confirmed coins before funding a wallet.
        node.make_block()
        node.make_block()
        mixed_case = "jc" + recipient[2:].upper()

        txid = node.request_test_faucet(mixed_case)

        self.assertEqual(len(txid), 64)
        self.assertTrue(node.get_account(recipient)["test_faucet_claimed"])
        self.assertEqual(node.get_account(recipient)["pending_in"], 100)
        with self.assertRaises(node.FaucetAlreadyClaimed):
            node.request_test_faucet(recipient)
        node.make_block()
        self.assertEqual(node.get_account(recipient)["balance"], 101)

    def test_rejected_pending_transaction_is_recorded_with_reason(self):
        sender_key = make_key()
        sender = self.fund(sender_key)
        recipient = "JC" + "a" * 40
        first = make_tx(sender_key, 5, 0, recipient)
        second = make_tx(sender_key, 6, 1, recipient)
        with node.LOCK, node.DB:
            for tx in (first, second):
                txid = node.sha256(node.canonical(tx).encode("ascii"))
                node.DB.execute("INSERT INTO pending VALUES(?,?)", (txid, node.canonical(tx)))

        result = node.make_block()

        self.assertEqual((result["confirmed"], result["rejected"]), (1, 1))
        history = node.transactions_for(sender)
        self.assertEqual({item["status"] for item in history}, {"confirmed", "rejected"})
        rejected = next(item for item in history if item["status"] == "rejected")
        self.assertIn("Not enough confirmed", rejected["reason"])
        self.assertEqual(node.DB.execute("SELECT COUNT(*) FROM pending").fetchone()[0], 0)

    def test_chain_passes_validation_after_process_reopen(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="jcoin-restart-test-") as temp:
            data_dir = Path(temp) / "node-data"
            restored_dir = Path(temp) / "restored-node-data"
            env = os.environ.copy()
            env["JCOIN_DATA_DIR"] = str(data_dir)
            create = (
                "import jcoin_node as node; node.initialize_chain(); "
                "node.make_block(); node.verify_chain(); node.DB.close()"
            )
            reopen = "import jcoin_node as node; node.verify_chain(); node.DB.close()"
            subprocess.run([sys.executable, "-c", create], cwd=root, env=env,
                           check=True, capture_output=True, text=True)
            shutil.copytree(data_dir, restored_dir, copy_function=shutil.copy2)
            for path in (data_dir, restored_dir):
                env["JCOIN_DATA_DIR"] = str(path)
                subprocess.run([sys.executable, "-c", reopen], cwd=root, env=env,
                               check=True, capture_output=True, text=True)

    def test_chain_check_rejects_signed_block_with_wrong_reward(self):
        node.make_block()
        row = node.DB.execute("SELECT * FROM blocks WHERE height=1").fetchone()
        block = json.loads(row["body"])
        block["reward"] -= 1
        body = node.canonical(block)
        block_hash = node.sha256(body.encode("ascii"))
        signature = base64.b64encode(node.MASTER_KEY.sign(bytes.fromhex(block_hash))).decode("ascii")
        with node.LOCK, node.DB:
            node.DB.execute("UPDATE blocks SET body=?,block_hash=?,signature=? WHERE height=1",
                            (body, block_hash, signature))
        with self.assertRaisesRegex(RuntimeError, "issuance schedule"):
            node.verify_chain()

    def test_whole_coin_reward_schedule_emits_less_than_declared_ceiling(self):
        # Height zero is an unrewarded genesis block. Right shifts truncate
        # each halving to whole coins, so the safety ceiling is not the target.
        scheduled = (node.HALVING_INTERVAL - 1) * node.reward_at(1)
        for period in range(1, 6):
            scheduled += node.HALVING_INTERVAL * node.reward_at(
                period * node.HALVING_INTERVAL)
        self.assertEqual(scheduled, 81_479_950)
        self.assertLess(scheduled, node.COIN_CAP)

    def test_failed_block_write_keeps_pending_transfer(self):
        key = make_key()
        self.fund(key)
        tx = make_tx(key, 1, 0, "JC" + "e" * 40)
        txid = node.sha256(node.canonical(tx).encode("ascii"))
        with node.LOCK, node.DB:
            node.DB.execute("INSERT INTO pending VALUES(?,?)", (txid, node.canonical(tx)))
            node.DB.execute("CREATE TRIGGER fail_block_insert BEFORE INSERT ON blocks "
                            "BEGIN SELECT RAISE(ABORT, 'simulated disk failure'); END")
        try:
            with self.assertRaisesRegex(sqlite3.IntegrityError, "simulated disk failure"):
                node.make_block()
            self.assertEqual(node.DB.execute("SELECT COUNT(*) FROM pending").fetchone()[0], 1)
            self.assertEqual(node.DB.execute("SELECT COUNT(*) FROM blocks").fetchone()[0], 3)
        finally:
            with node.LOCK, node.DB:
                node.DB.execute("DROP TRIGGER IF EXISTS fail_block_insert")

    @unittest.skipUnless(os.name == "posix", "POSIX file permissions are required")
    def test_existing_validator_key_and_data_directory_are_restricted(self):
        with tempfile.TemporaryDirectory(prefix="jcoin-key-permissions-") as temp:
            data_dir = Path(temp) / "node-data"
            data_dir.mkdir(mode=0o755)
            key_path = data_dir / "master-validator.key"
            key = make_key()
            raw = key.private_bytes(
                serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                serialization.NoEncryption())
            key_path.write_bytes(raw)
            os.chmod(data_dir, 0o755)
            os.chmod(key_path, 0o644)

            with mock.patch.object(node, "DATA", data_dir), mock.patch.object(node, "KEY_PATH", key_path):
                loaded = node.load_or_create_key()

            self.assertEqual(stat.S_IMODE(data_dir.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(key_path.stat().st_mode), 0o600)
            self.assertEqual(loaded.private_bytes(
                serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                serialization.NoEncryption()), raw)

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "O_NOFOLLOW is required")
    def test_symlink_validator_key_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="jcoin-key-symlink-") as temp:
            data_dir = Path(temp) / "node-data"
            data_dir.mkdir(mode=0o700)
            target = data_dir / "elsewhere.key"
            target.write_bytes(b"x" * 32)
            key_path = data_dir / "master-validator.key"
            key_path.symlink_to(target)
            with mock.patch.object(node, "DATA", data_dir), mock.patch.object(node, "KEY_PATH", key_path):
                with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                    node.load_or_create_key()

    def test_database_integrity_failure_stops_startup_validation(self):
        class DamagedDatabase:
            def execute(self, statement):
                self.asserted_statement = statement
                return self

            def fetchall(self):
                return [("*** in database blocks ***",)]

        damaged = DamagedDatabase()
        with mock.patch.object(node, "DB", damaged):
            with self.assertRaisesRegex(RuntimeError, "database integrity check failed"):
                node.verify_database_integrity()
        self.assertEqual(damaged.asserted_statement, "PRAGMA quick_check")

    def test_admin_origin_gate_rejects_missing_and_untrusted_origins(self):
        allowed = node.local_operator_allowed
        self.assertTrue(allowed("127.0.0.1", "http://127.0.0.1:8765"))
        self.assertTrue(allowed("127.0.0.1", "http://localhost:8765"))
        self.assertFalse(allowed("127.0.0.1", None))
        self.assertFalse(allowed("127.0.0.1", "https://attacker.example"))
        self.assertFalse(allowed("192.0.2.10", "http://127.0.0.1:8765"))
        self.assertTrue(allowed("127.0.0.1", None, allow_missing_origin=True))


if __name__ == "__main__":
    unittest.main()
