# Native wallet

Start the node with `./run-jcoin.sh`, then launch `./run-wallet.sh` or open
`JCoin-Wallet.desktop`. The GTK4 app connects to `http://127.0.0.1:8765` by
default.

Create a wallet with a password of at least 12 characters and confirm it when
prompted. The Ed25519 private key is saved as a password-encrypted
`.jcoinwallet` file under
`~/.local/share/jcoin-wallet` with owner-only file permissions. New native
wallet backups use the same versioned format as the browser wallets and can be
opened by the dashboard or standalone wallet. Keep a copy outside the
computer, store the password separately, and remember it; JCoin cannot recover
a lost password.

The native wallet can also open old native `.jcoinwallet` files. When it does,
it preserves the old file and writes a separate browser-compatible encrypted
copy to `~/.local/share/jcoin-wallet`.

Python dependencies are listed in `requirements.txt`. GTK4 and PyGObject must
also be installed through the operating system's package manager.

This is an experimental single-validator prototype. The ledger exposes sender addresses, recipient addresses, and amounts; encrypted key storage does not make transactions private. Use test coins only.

The send form selects **Private (default)**, but private transfers are not
implemented. To send a prototype transfer, explicitly select **Transparent
test send** and confirm the warning; transaction details are visible to the
node and anyone who can inspect its ledger.
