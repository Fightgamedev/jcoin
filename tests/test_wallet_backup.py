import base64
import hashlib
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from jcoin_backup import (
    CIPHER,
    FORMAT,
    KDF,
    VERSION,
    address_for,
    create_backup,
    open_backup,
    open_legacy_native_backup,
)

ROOT = Path(__file__).resolve().parents[1]
NODE_SCRIPT = ROOT / "tests" / "wallet_backup_webcrypto.mjs"
PASSWORD = "test-only-password-never-reuse"


def encoded(raw):
    return base64.b64encode(raw).decode("ascii")


def public_bytes(private_key):
    return private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


class WalletBackupTests(unittest.TestCase):
    def setUp(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.backup = create_backup(self.private_key, PASSWORD, "Test wallet")

    def test_shared_format_round_trip_and_required_fields(self):
        self.assertEqual(self.backup["format"], FORMAT)
        self.assertEqual(self.backup["version"], VERSION)
        self.assertEqual(self.backup["kdf"], KDF)
        self.assertEqual(self.backup["cipher"], CIPHER)
        self.assertEqual(public_bytes(open_backup(self.backup, PASSWORD)), public_bytes(self.private_key))

    def test_wrong_password_is_rejected(self):
        with self.assertRaises(InvalidTag):
            open_backup(self.backup, "incorrect-password")

    def test_non_text_password_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "password must be text"):
            open_backup(self.backup, None)

    def test_changed_address_is_rejected(self):
        damaged = dict(self.backup)
        damaged["address"] = "JC" + "0" * 40
        with self.assertRaisesRegex(ValueError, "does not match"):
            open_backup(damaged, PASSWORD)

    def test_damaged_ciphertext_is_rejected(self):
        damaged = dict(self.backup)
        raw = bytearray(base64.b64decode(damaged["encryptedPrivateKey"]))
        raw[-1] ^= 1
        damaged["encryptedPrivateKey"] = encoded(raw)
        with self.assertRaises(InvalidTag):
            open_backup(damaged, PASSWORD)

    def test_unknown_version_is_rejected(self):
        damaged = dict(self.backup)
        damaged["version"] = 2
        with self.assertRaisesRegex(ValueError, "version"):
            open_backup(damaged, PASSWORD)

    def test_legacy_native_backup_can_be_opened(self):
        raw_private = self.private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        salt = os.urandom(16)
        nonce = os.urandom(12)
        wrapping_key = hashlib.pbkdf2_hmac("sha256", PASSWORD.encode(), salt, 310_000, 32)
        legacy = {
            "version": 1,
            "salt": encoded(salt),
            "nonce": encoded(nonce),
            "key": encoded(AESGCM(wrapping_key).encrypt(nonce, raw_private, None)),
        }
        restored = open_legacy_native_backup(legacy, PASSWORD)
        self.assertEqual(address_for(public_bytes(restored)), address_for(public_bytes(self.private_key)))
        migrated = create_backup(restored, PASSWORD, "Migrated native wallet")
        migrated_key = open_backup(migrated, PASSWORD)
        self.assertEqual(address_for(public_bytes(migrated_key)), address_for(public_bytes(self.private_key)))

    def test_invalid_base64_is_rejected(self):
        damaged = dict(self.backup)
        damaged["salt"] = "not valid base64!"
        with self.assertRaisesRegex(ValueError, "base64"):
            open_backup(damaged, PASSWORD)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for browser WebCrypto interoperability checks")
    def test_python_backup_opens_with_browser_webcrypto(self):
        result = subprocess.run(
            ["node", str(NODE_SCRIPT), "open"],
            input=json.dumps({"backup": self.backup, "password": PASSWORD}),
            text=True,
            capture_output=True,
            check=True,
        )
        opened = json.loads(result.stdout)
        self.assertEqual(base64.b64decode(opened["privateKeyDer"]), self.private_key.private_bytes(
            Encoding.DER, PrivateFormat.PKCS8, NoEncryption()))

    @unittest.skipUnless(shutil.which("node"), "Node.js is required for browser WebCrypto interoperability checks")
    def test_browser_webcrypto_backup_opens_in_python(self):
        result = subprocess.run(
            ["node", str(NODE_SCRIPT), "create"],
            input=json.dumps({"password": PASSWORD, "name": "Browser test wallet"}),
            text=True,
            capture_output=True,
            check=True,
        )
        backup = json.loads(result.stdout)
        self.assertEqual(backup["address"], address_for(base64.b64decode(backup["publicKey"])))
        restored = open_backup(backup, PASSWORD)
        self.assertEqual(public_bytes(restored), base64.b64decode(backup["publicKey"]))


if __name__ == "__main__":
    unittest.main()
