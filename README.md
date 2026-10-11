# JCoin prototype

JCoin now runs as a centrally operated, single-validator test prototype. Your laptop runs the node, stores the chain, validates signed wallet transfers, and signs each new block. When the node is stopped, transfers cannot be confirmed.

## Start the node

Double-click JCoin.desktop. If Linux Mint asks whether to trust or launch the file, choose Allow Launching. A terminal runs the node and the Jcoin home page opens at http://127.0.0.1:8765. Choose **Open local wallet** to enter the dashboard at http://127.0.0.1:8765/dashboard. Keep the terminal open while using Jcoin; close it to stop the node.

You can also run ./run-jcoin.sh from this folder. The first start creates node-data/jcoin.sqlite3 and node-data/master-validator.key. The master key is the validator identity and controls the master wallet. Keep the key private and make a secure backup.

Create a browser wallet in the dashboard to receive or send coins. Its personal signing key stays in that browser's IndexedDB; the node receives only public keys and signed transactions. The standalone browser wallet and native GTK wallet are separate clients. See [the browser wallet guide](docs/BROWSER-CLIENT-README.md) and [the native wallet guide](docs/NATIVE-CLIENT-README.md).

## Requirements

- Python 3 and the `cryptography` package (`python3 -m pip install -r requirements.txt`).
- For the native wallet, GTK4 and PyGObject are also required from the operating system.
- For the dashboard and standalone wallet, use a modern browser. The standalone wallet uses browser cryptography APIs.

## Project layout

- `jcoin_node.py`: loopback node, transaction validation, and block signing.
- `index.html`: bilingual Jcoin landing page and staged product roadmap.
- `dashboard.html`: local node dashboard and browser wallet.
- `JCoin-Wallet.html`: standalone encrypted-backup browser wallet.
- `jcoin_wallet.py`: native GTK wallet.
- `run-jcoin.sh`, `run-wallet.sh`: launch scripts.
- `docs/`: client instructions and project continuation notes.
- `node-data/`: local chain and validator key, generated at first start and excluded from Git.

Rebuild the standalone wallet bundle with `./build-client.sh` after changing its page or guide.

## Milestones

The goal is to grow JCoin from a local wallet prototype toward a simple everyday payment experience. Milestones are sequenced by dependency; future features are ideas, not delivery promises. JCoin remains test-only until the final review is complete.

- [x] **Milestone 0 — Local prototype:** Run one local validator, create wallets, sign and queue transfers, confirm them in blocks, and inspect balances and activity.
- [ ] **Milestone 1 — Wallet safety and recovery:** Define one wallet format for the browser and native clients; add encrypted export, import, and restore; verify a restored wallet address before use; document backup and recovery steps.
- [ ] **Milestone 2 — Protocol correctness:** Add automated coverage for transaction signatures, nonces, duplicate submissions, overspending, block rewards, and the supply cap. Validate all stored blocks and transactions at startup, and make database writes atomic under concurrent requests.
- [ ] **Milestone 3 — Everyday person-to-person payments:** Improve the mobile send and receive flow; add receive QR codes or payment links, clear pending and confirmed states, and useful transaction receipts. Keep QR data bound to the intended recipient and amount where applicable.
- [ ] **Milestone 4 — Merchant test flow:** In a test environment, explore merchant-presented QR checkout, payment confirmation, refunds, and basic merchant records. Do not connect real funds.
- [ ] **Milestone 5 — Production readiness review:** Before any remote or real-money use, complete independent security and privacy reviews, operational recovery planning, and qualified legal and regulatory review for the intended markets. This milestone is a review gate, not a launch commitment.

Top-ups, cash-outs, rewards, and a public network are out of scope until earlier milestones are complete and separately reviewed.

## What this is

This is a small, centrally operated blockchain prototype. Blocks are linked by SHA-256 hashes and signed by the one validator key on your laptop. User transfers use Ed25519 signatures. The issuance defaults are Litecoin-like (50 JCOIN per block, halving every 840,000 blocks, 84,000,000 cap); they are prototype settings, not a launch specification.

This is not Bitcoin or Litecoin consensus and is not decentralized: users trust your validator, and one machine controls block production. The current version listens only on your own laptop. It has not been reviewed for security and JCOIN has no real-world value. Do not expose the node to the internet or use real funds.
