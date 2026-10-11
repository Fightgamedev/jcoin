# Project notes

## Current shape

- `jcoin_node.py` runs a loopback-only HTTP node and validator.
- `index.html` is the bilingual project landing page hosted by the node.
- `dashboard.html` is the local dashboard and browser wallet.
- `jcoin_codeq.py` is an isolated CodeQ allocation prototype, not wired into transfers.
- `JCoin-Wallet.html` is a standalone browser wallet for a compatible node.
- `jcoin_wallet.py` is the GTK4 native wallet.
- `run-jcoin.sh` and `run-wallet.sh` are the shell launchers.
- `node-data/` is generated local state. It contains the validator key and must never be committed or shared.

## Protocol details

- Addresses are `JC` followed by the first 40 lowercase hexadecimal characters of SHA-256(public key).
- Transactions are canonical JSON signed with Ed25519.
- The node is a centrally operated, single-validator prototype, not decentralized consensus.
- Current transactions expose sender, recipient, and amount in cleartext. No private-payment cryptography is implemented.
- The node binds to `127.0.0.1:8765`; remote access is not supported or safe to enable without a separate security review.

## Before continuing development

- Keep generated chain data, validator keys, wallet backups, and credentials out of Git.
- Update `README.md` when launch steps or dependencies change.
- Keep the browser and native wallet address and signing formats aligned with the node.
- The HTML wallet bundle should be refreshed whenever its page or client instructions change.
- Avoid treating balances or the prototype issuance schedule as real funds or a production monetary policy.

## Known limitations

- The chain has one trusted validator and no peer-to-peer networking or consensus.
- QR payments, merchant checkout, top-ups, rewards, and split bills are roadmap ideas only; none are implemented.
- CodeQ uses deterministic integer apportionment for multi-recipient allocation; it is not yet signed, replay-protected, privacy-preserving, or settled by the node. Its SHA-256 hash is not encryption.
- The node's storage and API have not had a security audit.
- The native client requires GTK4 and PyGObject from the operating system in addition to Python packages.
- No automated test suite is currently included.
