# Project notes

## Current shape

- `jcoin_node.py` runs a loopback-only HTTP node and validator.
- `index.html` is the bilingual project landing page hosted by the node.
- `dashboard.html` is the local dashboard and browser wallet.
- New dashboard, standalone browser, and native wallets share a password-encrypted `.jcoinwallet` format. The native client still reads its legacy format and writes a compatible copy; older dashboard wallets without a saved backup use non-extractable keys and cannot be exported by the dashboard.
- `jcoin_codeq.py` is an isolated CodeQ allocation prototype, not wired into transfers.
- `jcoin_backup.py` defines the shared password-encrypted wallet backup format; `tests/` checks it against native cryptography and browser-style WebCrypto.
- `docs/FIRST-RELEASE.md` records the provisional Japan-first test audience and local desktop scope; it is a product learning target, not a public launch promise.
- `JCoin-Wallet.html` is a standalone browser wallet for a compatible node.
- `jcoin_wallet.py` is the GTK4 native wallet.
- `run-jcoin.sh` and `run-wallet.sh` are the shell launchers.
- `node-data/` is generated local state. It contains the validator key and must never be committed or shared.

## Protocol details

- Addresses are `JC` followed by the first 40 lowercase hexadecimal characters of SHA-256(public key).
- Transactions are canonical JSON signed with Ed25519.
- The node is a centrally operated, single-validator prototype, not decentralized consensus.
- Current transactions expose sender, recipient, and amount in cleartext. No private-payment cryptography is implemented.
- The initial privacy threat-model draft is in `docs/PRIVACY-THREAT-MODEL.md`. It records unresolved decisions and must be updated when data flows change.
- `docs/PRIVACY-PROTOCOL-EVALUATION.md` is an early model comparison and decision checklist, not a selection or endorsement. Do not implement a new privacy protocol from it.
- `docs/JCOIN-EXPLICIT-PRIVACY-PROTOCOL.md` proposes private-by-default, explicit transparent opt-in, and no automatic downgrade. It is not cryptographically specified; the dashboard selector is only a UX preview because the node currently sends cleartext transfers.
- A future goal is to let people run nodes on their computers and earn rewards for verifiable network service. The design sketch and current limitations are in `docs/NETWORK-INCENTIVES.md`.
- Node request logs omit query strings to avoid copying balance-query addresses into terminal logs. The address is still sent in the local HTTP request.
- `/api/pending` returns full cleartext transactions only after the loopback/Origin check, which is not general authentication. Wildcard CORS remains a limitation to resolve before any remote or sensitive use.
- The node binds to `127.0.0.1:8765`; remote access is not supported or safe to enable without a separate security review.

## Before continuing development

- Keep generated chain data, validator keys, wallet backups, and credentials out of Git.
- Update `README.md` when launch steps or dependencies change.
- Keep the browser and native wallet address and signing formats aligned with the node.
- The HTML wallet bundle should be refreshed whenever its page or client instructions change.
- Avoid treating balances or the prototype issuance schedule as real funds or a production monetary policy.

## Known limitations

- The chain has one trusted validator and no peer-to-peer networking or consensus.
- QR payments, merchant checkout, top-ups, split bills, a public peer-to-peer network, and rewards for node operators are roadmap ideas only; none are implemented. The current block reward goes to the local validator wallet, not to other computers.
- CodeQ uses deterministic integer apportionment for multi-recipient allocation; it is not yet signed, replay-protected, privacy-preserving, or settled by the node. Its SHA-256 hash is not encryption.
- The node's storage and API have not had a security audit.
- The native client requires GTK4 and PyGObject from the operating system in addition to Python packages.
- `python3 -m unittest discover -s tests -v` runs encrypted-wallet backup checks. Node.js is optional; cross-runtime WebCrypto checks are skipped when it is unavailable. These are not a chain or privacy-protocol test suite.
