# JCoin prototype

JCoin now runs as a centrally operated, single-validator test prototype. Your laptop runs the node, stores the chain, validates signed wallet transfers, and signs each new block. When the node is stopped, transfers cannot be confirmed.

## Start the node

Double-click JCoin.desktop. If Linux Mint asks whether to trust or launch the file, choose Allow Launching. A terminal runs the node and the dashboard opens at http://127.0.0.1:8765. Keep that terminal open while using JCoin; close it to stop the node.

You can also run ./run-jcoin.sh from this folder. The first start creates node-data/jcoin.sqlite3 and node-data/master-validator.key. The master key is the validator identity and controls the master wallet. Keep the key private and make a secure backup.

Create a browser wallet in the dashboard to receive or send coins. Its personal signing key stays in that browser's IndexedDB; the node receives only public keys and signed transactions. The standalone browser wallet and native GTK wallet are separate clients. See [the browser wallet guide](docs/BROWSER-CLIENT-README.md) and [the native wallet guide](docs/NATIVE-CLIENT-README.md).

## Requirements

- Python 3 and the `cryptography` package (`python3 -m pip install -r requirements.txt`).
- For the native wallet, GTK4 and PyGObject are also required from the operating system.
- For the dashboard and standalone wallet, use a modern browser. The standalone wallet uses browser cryptography APIs.

## Project layout

- `jcoin_node.py`: loopback node, transaction validation, and block signing.
- `index.html`: node dashboard and browser wallet.
- `JCoin-Wallet.html`: standalone encrypted-backup browser wallet.
- `jcoin_wallet.py`: native GTK wallet.
- `run-jcoin.sh`, `run-wallet.sh`: launch scripts.
- `docs/`: client instructions and project continuation notes.
- `node-data/`: local chain and validator key, generated at first start and excluded from Git.

Rebuild the standalone wallet bundle with `./build-client.sh` after changing its page or guide.

## What this is

This is a small, centrally operated blockchain prototype. Blocks are linked by SHA-256 hashes and signed by the one validator key on your laptop. User transfers use Ed25519 signatures. The issuance defaults are Litecoin-like (50 JCOIN per block, halving every 840,000 blocks, 84,000,000 cap); they are prototype settings, not a launch specification.

This is not Bitcoin or Litecoin consensus and is not decentralized: users trust your validator, and one machine controls block production. The current version listens only on your own laptop. It has not been reviewed for security and JCOIN has no real-world value. Do not expose the node to the internet or use real funds.
