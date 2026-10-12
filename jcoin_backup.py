"""Shared JCoin wallet backup format helpers (not transaction privacy)."""
import base64
import binascii
import hashlib
import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_der_private_key,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

FORMAT = "jcoin-wallet"
VERSION = 1
KDF = "PBKDF2-SHA256-310000"
CIPHER = "AES-256-GCM"
ITERATIONS = 310_000


def _b64decode(value, field):
    if not isinstance(value, str):
        raise ValueError(f"Backup field {field} must be base64 text.")
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError(f"Backup field {field} is invalid base64.") from exc


def address_for(public_key):
    return "JC" + hashlib.sha256(public_key).hexdigest()[:40]


def create_backup(private_key, password, name="JCoin wallet"):
    """Create the versioned encrypted format shared by all JCoin clients."""
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("JCoin backups require an Ed25519 private key.")
    if not isinstance(password, str) or not password:
        raise ValueError("A non-empty backup password is required.")
    salt = os.urandom(16)
    iv = os.urandom(12)
    wrapping_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS, 32)
    private_der = private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
    encrypted = AESGCM(wrapping_key).encrypt(iv, private_der, None)
    public_key = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {
        "format": FORMAT,
        "version": VERSION,
        "name": str(name)[:32],
        "address": address_for(public_key),
        "publicKey": base64.b64encode(public_key).decode("ascii"),
        "kdf": KDF,
        "cipher": CIPHER,
        "salt": base64.b64encode(salt).decode("ascii"),
        "iv": base64.b64encode(iv).decode("ascii"),
        "encryptedPrivateKey": base64.b64encode(encrypted).decode("ascii"),
    }


def open_backup(backup, password):
    """Decrypt and validate a shared-format backup before exposing its key."""
    if not isinstance(password, str):
        raise ValueError("Wallet password must be text.")
    if not isinstance(backup, dict) or backup.get("format") != FORMAT:
        raise ValueError("This is not a JCoin wallet backup.")
    if type(backup.get("version")) is not int or backup["version"] != VERSION:
        raise ValueError("Unsupported JCoin wallet backup version.")
    if backup.get("kdf") != KDF or backup.get("cipher") != CIPHER:
        raise ValueError("Unsupported JCoin wallet backup encryption settings.")
    salt = _b64decode(backup.get("salt"), "salt")
    iv = _b64decode(backup.get("iv"), "iv")
    encrypted = _b64decode(backup.get("encryptedPrivateKey"), "encryptedPrivateKey")
    public_key = _b64decode(backup.get("publicKey"), "publicKey")
    if len(salt) != 16 or len(iv) != 12 or len(public_key) != 32:
        raise ValueError("JCoin backup contains invalid key or nonce lengths.")
    wrapping_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS, 32)
    private_der = AESGCM(wrapping_key).decrypt(iv, encrypted, None)
    private_key = load_der_private_key(private_der, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("JCoin backup does not contain an Ed25519 key.")
    actual_public = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    if actual_public != public_key or address_for(actual_public) != backup.get("address"):
        raise ValueError("Backup key does not match its public key and address.")
    if not isinstance(backup.get("name"), str):
        raise ValueError("JCoin backup name is invalid.")
    return private_key


def open_legacy_native_backup(backup, password):
    """Read the original GTK wallet format so it can be migrated safely."""
    if not isinstance(password, str):
        raise ValueError("Wallet password must be text.")
    if not isinstance(backup, dict) or type(backup.get("version")) is not int or backup["version"] != 1:
        raise ValueError("Unsupported legacy native wallet backup.")
    salt = _b64decode(backup.get("salt"), "salt")
    nonce = _b64decode(backup.get("nonce"), "nonce")
    encrypted = _b64decode(backup.get("key"), "key")
    if len(salt) != 16 or len(nonce) != 12:
        raise ValueError("Legacy wallet backup contains invalid salt or nonce lengths.")
    wrapping_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS, 32)
    raw_key = AESGCM(wrapping_key).decrypt(nonce, encrypted, None)
    if len(raw_key) != 32:
        raise ValueError("Legacy wallet backup contains an invalid key.")
    return Ed25519PrivateKey.from_private_bytes(raw_key)
