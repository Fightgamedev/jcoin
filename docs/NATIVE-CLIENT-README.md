# Native wallet

Start the node with `./run-jcoin.sh`, then launch `./run-wallet.sh` or open
`JCoin-Wallet.desktop`. The GTK4 app connects to `http://127.0.0.1:8765` by
default.

Create a wallet with a password of at least 8 characters. The Ed25519 private
key is encrypted with AES-GCM using a PBKDF2-HMAC-SHA256-derived key and saved
under `~/.local/share/jcoin-wallet` with owner-only file permissions. Keep a
separate secure backup and remember the password; the node cannot recover it.

Python dependencies are listed in `requirements.txt`. GTK4 and PyGObject must
also be installed through the operating system's package manager.

This is an experimental single-validator prototype. Use test coins only.
