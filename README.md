# JCoin prototype

JCoin currently runs as a centrally operated, single-validator test prototype. Its ledger is transparent: sender addresses, recipient addresses, and amounts are stored in cleartext. Privacy is a future protocol goal; the current wallet and CodeQ arithmetic spike do not provide private transactions. When the node is stopped, transfers cannot be confirmed.

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
- `jcoin_codeq.py`: CodeQ's transparent deterministic allocation spike; it does not submit payments or hide transaction details.
- `jcoin_backup.py`: shared encrypted wallet-backup format and validation used by the native wallet.
- `tests/`: automated backup-format and Python/WebCrypto interoperability checks.
- `run-jcoin.sh`, `run-wallet.sh`: launch scripts.
- `docs/`: client instructions, project notes, and [the CodeQ design](docs/CODEQ.md).
- [Initial privacy threat model](docs/PRIVACY-THREAT-MODEL.md): current data exposure, assumptions, goals, and open decisions.
- [Privacy protocol evaluation](docs/PRIVACY-PROTOCOL-EVALUATION.md): early Monero and Zcash model comparison and decision criteria; no protocol selected.
- [Explicit privacy-mode protocol proposal](docs/JCOIN-EXPLICIT-PRIVACY-PROTOCOL.md): private-by-default design with a deliberate transparent option and fail-closed rules; research only.
- [First release scope](docs/FIRST-RELEASE.md): initial audience, local test release tasks, acceptance goal, and explicit exclusions.
- [Network participation rewards](docs/NETWORK-INCENTIVES.md): a proposed path for rewarding people who run JCoin nodes; no public network or node rewards exist today.
- `AGENTS.md` and `.github/agents/`: shared coding-agent rules and specialist roles. Start with the [beginner's guide to agents](docs/AGENTS-GUIDE.md).
- `node-data/`: local chain and validator key, generated at first start and excluded from Git.

Rebuild the standalone wallet bundle with `./build-client.sh` after changing its page or guide.

## Development checks

Run the wallet-backup checks with:

```sh
python3 -m unittest discover -s tests -v
```

The Python/native checks use the project requirements. The browser WebCrypto
interoperability checks also use Node.js; Python skips those two checks when
Node.js is unavailable. These checks cover backup serialization and recovery,
not payment privacy or blockchain consensus.

## Working with AI agents

The repository includes reusable roles for coordinating project work, privacy
design, implementation, and security review. They are helpers—not automatic
proof of correctness or security. Read the [beginner's guide](docs/AGENTS-GUIDE.md)
before trying a multi-agent task; all agents must follow [AGENTS.md](AGENTS.md).

## Milestones

The goal is to grow JCoin from a local wallet prototype toward privacy-first everyday payments. Milestones are sequenced by dependency; future features are ideas, not delivery promises. JCoin remains test-only until the final review is complete.

- [x] **Milestone 0 — Local prototype:** Run one local validator, create wallets, sign and queue transfers, confirm them in blocks, and inspect balances and activity.
- [ ] **Milestone 1 — Privacy threat model and protocol evaluation:** Define what the public, validator, recipient, wallet provider, and network observer can learn, then evaluate complete protocol models against those needs. See [the threat model](docs/PRIVACY-THREAT-MODEL.md), [the early comparison](docs/PRIVACY-PROTOCOL-EVALUATION.md), and [the explicit privacy-mode proposal](docs/JCOIN-EXPLICIT-PRIVACY-PROTOCOL.md). No cryptographic protocol is selected.
- [x] **Milestone 1a — CodeQ allocation spike:** Define a declarative payment intent and deterministic integer allocation rule that conserves the full amount across recipients. The current compiler prints cleartext data; its hash is not hiding, and it is not connected to the wallet.
- [ ] **Milestone 2 — Shielded protocol and correctness:** Prototype private notes, hidden values and recipients, double-spend prevention, and a proof that inputs equal outputs plus fees while satisfying CodeQ rules. Use established cryptography, add automated coverage, validate stored history at startup, and make database writes atomic under concurrent requests.
- [ ] **Milestone 3 — Wallet safety and selective disclosure:** Align encrypted wallet backup and restore across clients, preserve older backups during migration, then design spend and viewing keys, recipient verification, and payment proofs that reveal only selected details. New dashboard and native backups now share the standalone wallet format; older dashboard keys cannot be exported.
- [ ] **Milestone 4 — Everyday private payments:** Improve mobile send and receive; add private receive QR codes or payment requests, clear pending and confirmed states, and useful private receipts.
- [ ] **Milestone 5 — Private merchant test flow:** In a test environment, explore QR checkout, merchant confirmation, refunds, and basic records without publishing user purchase histories or connecting real funds.
- [ ] **Milestone 6 — Distributed network and participation rewards:** Design and test peer discovery, independent validation, reliable node operation, and a capped reward policy. Reward useful, independently verifiable service; do not pay for a node's own uptime report. See [docs/NETWORK-INCENTIVES.md](docs/NETWORK-INCENTIVES.md). This work depends on protocol, privacy, and Sybil-resistance reviews.
- [ ] **Milestone 7 — Production readiness review:** Before remote or real-money use, complete independent security and privacy reviews, operational recovery planning, and qualified legal and regulatory review for intended markets. This is a review gate, not a launch commitment.

## Next work queue

These are the next concrete tasks, ordered by safety and dependency. The first item is complete; the remaining items are open product and architecture work.

- [x] **Verify wallet backup interoperability:** Automated round-trip checks cover the shared browser/native backup format, wrong passwords, damaged metadata, and legacy native-file migration.
- [x] **Choose the first audience and platform:** Start with Japanese-speaking, non-technical desktop testers of the local prototype; remote and mobile-only use wait for network and privacy readiness. See [first release scope](docs/FIRST-RELEASE.md).
- [x] **Simplify first-run wallet guidance:** The local dashboard now supports Japanese and English, remembers the language choice, and presents the wallet setup, receive, backup, and privacy limitations in both languages.
- [ ] **Settle the privacy architecture:** Compare maintained protocol implementations and their full wallet/consensus requirements; require expert review before protocol implementation. Do not invent cryptographic primitives.
- [x] **Define a small first release:** Scope wallet creation/recovery, receiving, explicitly transparent test sending, and honest confirmation states for the selected audience. See [first release scope](docs/FIRST-RELEASE.md).
- [ ] **Keep node rewards behind network design:** First build peer-to-peer validation and a reviewed way to measure useful service; do not reward self-reported uptime.

Top-ups, cash-outs, merchant payments, network participation rewards, and a public network are future goals only. They are not supported until the prerequisite design, implementation, and independent reviews are complete.

### CodeQ experiment

CodeQ (Conserved-Quanta Payment Code) is a proposed declarative language for expressing payment rules that a privacy proof can enforce. The current arithmetic compiler is a transparent experiment, not private-payment software. See [docs/CODEQ.md](docs/CODEQ.md) for the proposed shielded design and limitations. The name is not globally unique, and the underlying arithmetic is not claimed as new mathematics.

## What this is

This is a small, centrally operated blockchain prototype. Blocks are linked by SHA-256 hashes and signed by the one validator key on your laptop. User transfers use Ed25519 signatures. The issuance defaults are Litecoin-like (50 JCOIN per block, halving every 840,000 blocks, 84,000,000 cap); they are prototype settings, not a launch specification.

This is not Bitcoin or Litecoin consensus and is not decentralized: users trust your validator, and one machine controls block production. The current version listens only on your own laptop. The dashboard defaults to a private-send choice, but private sending is not implemented; a transfer is only sent after explicitly choosing transparent test mode. Its prototype block reward goes to the local validator wallet; it does not reward other computers or measure uptime. Transaction details are visible in its ledger and it has not been reviewed for security or privacy. JCOIN has no real-world value. Do not expose the node to the internet or use real funds.
