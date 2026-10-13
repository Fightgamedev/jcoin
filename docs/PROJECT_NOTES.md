# Project notes

## Current shape

- `jcoin_node.py` runs a loopback-only HTTP node and validator.
- Startup checks SQLite structure and validates each block's signature, link,
  transaction signatures, nonce order, balances, reward schedule, and supply
  ceiling. Damaged storage fails closed; there is no automatic repair.
- On POSIX systems, the node restricts its data directory and existing
  validator-key file to owner-only permissions and rejects symlinked key paths.
  The key remains raw and unencrypted at rest, so this does not protect against
  malware running as the same user.
- The dashboard can request a one-time 100-JCOIN test transfer per browser-wallet address; the node stores transfer acceptance/rejection history for local display. Test coins have no value.
- `index.html` is the bilingual project landing page hosted by the node.
- `dashboard.html` is the local dashboard and browser wallet.
- New dashboard, standalone browser, and native wallets share a password-encrypted `.jcoinwallet` format. The native client still reads its legacy format and writes a compatible copy; older dashboard wallets without a saved backup use non-extractable keys and cannot be exported by the dashboard.
- `jcoin_codeq.py` is an isolated CodeQ allocation prototype, not wired into transfers.
- `jcoin_backup.py` defines the shared password-encrypted wallet backup format; `tests/` checks it against native cryptography and browser-style WebCrypto.
- `docs/FIRST-RELEASE.md` records the provisional Japan-first test audience and local desktop scope; it is a product learning target, not a public launch promise.
- The local dashboard has a Japanese/English language switch and defaults based on browser language; keep both translations aligned when changing the wallet flow.
- `JCoin-Wallet.html` is a standalone browser wallet for a compatible node.
- `jcoin_wallet.py` is the GTK4 native wallet.
- `run-jcoin.sh` and `run-wallet.sh` are the shell launchers.
- `node-data/` is generated local state. It contains the validator key and must never be committed or shared.
- [Node recovery guide](NODE-RECOVERY.md) documents a clean-stop full-directory backup and a restore that preserves the previous data. The key remains unencrypted at rest.

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
- Master-wallet sends, faucet claims, and block validation require an explicit
  trusted loopback browser Origin. This is only a browser request safeguard;
  local software can forge the header, so it is not operator authentication.
- SQLite access is synchronized across this process's HTTP threads. It is not a
  multi-process concurrency design.
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
- `python3 -m unittest discover -s tests -v` runs wallet backup, isolated
  ledger/faucet/rejection/restart, CodeQ allocation, issuance schedule,
  database integrity, and POSIX key-permission regression checks. Node.js is
  optional; cross-runtime WebCrypto checks are skipped when it is unavailable.
  These are not a full chain, consensus, or privacy-protocol test suite.
