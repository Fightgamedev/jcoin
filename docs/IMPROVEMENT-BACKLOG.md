# JCoin improvement backlog

This backlog comes from a review of the local prototype. It separates
immediate usability and correctness work from protocol and production work.
Nothing here changes the current test-only status or promises a launch date.

## Active: finish local test-flow review

- [x] Give a new browser wallet an obvious way to
  request one capped 100-coin test transfer from the local node wallet. The
  node enforces one request per address; coins have no value.
- [x] Show pending, confirmed, and rejected
  transfers for the selected wallet, including amount, other address, time,
  and an actionable rejection reason. A queued transfer is not described as
  confirmed.
- [x] Preserve and report rejected queued
  transfers when a block is made instead of silently deleting them.
- [ ] Manually verify Japanese and English dashboard behavior after the recent
  language-switch change, including first-run, backup restore, privacy choice,
  and narrow-screen layout.
- [ ] Add automated coverage for faucet claims, rejected transfers, and restart
  recovery. Ledger validation, confirmation, nonce replay, and failed-write
  rollback now have isolated automated coverage.

## Correctness and local key recovery

- [x] At startup, check transaction signatures and ledger semantics in every
  stored block: nonce order, available balances, reward schedule, and supply
  cap, in addition to block links, hashes, and validator signatures.
- [ ] Document a safe backup and restore procedure for the node database and
  validator key. The validator key is stored as raw bytes protected by local
  file permissions, not encrypted at rest.
- [x] Synchronize shared SQLite reads and writes across local HTTP worker
  threads, and commit each block plus its pending/rejected/faucet updates as
  one transaction. This remains a single-process local prototype; it is not a
  multi-process or public-node concurrency design.
- [x] Reject transaction fields that are not covered by the transaction
  signature, preventing unsigned metadata from being accepted into blocks.
- [x] Require a trusted loopback browser Origin for master-wallet, faucet, and
  block-validation POST actions; permit missing Origin only for local reads.
- [ ] Add real local operator authentication before the node handles value or
  sensitive data. Origin checks help against browser cross-origin requests but
  can be forged by local software and are not authentication.
- [x] Run SQLite `quick_check` before ledger validation and stop startup on
  structural corruption. The node does not repair damaged data automatically.
- [ ] Break large HTML, CSS, JavaScript, and compressed Python functions into
  reviewable pieces without changing the protocol format accidentally.
- [ ] Add a smallest currency unit. The current ledger and clients accept only
  whole JCOIN values; changing this requires an explicit versioned monetary
  rule and a safe migration plan, so it is not an in-place code change.
- [ ] Decide whether the emission target should be 84 million or the current
  whole-coin schedule's maximum of 81,479,950. Integer right-shift halvings
  truncate rewards, so the declared ceiling is not attained; do not alter
  historical issuance without a versioned protocol decision.
- [x] Restrict the node data directory and validator key to owner-only
  permissions on POSIX systems when loading an existing key, and reject
  symlinked/non-regular key paths.
- [ ] Protect the validator key from same-account compromise and document a
  tested database/key backup and restore workflow. The raw key is not encrypted
  at rest; POSIX file permissions do not protect against malware running as the
  wallet's user.
- [ ] Render all data received from configurable node endpoints as text, and
  review browser clients for hostile-node behavior. The optional wallet's
  block history was changed to use text nodes; a full client review remains.

## Privacy and network: research gates, not implementation promises

- [ ] Select a privacy design only after comparing maintained implementations,
  wallet requirements, validator visibility, metadata leakage, recovery, and
  independent expert review. Current transfers reveal sender, recipient, and
  amount; the private selector is a fail-closed UI choice, not a privacy
  feature.
- [ ] Design peer discovery, independent consensus, node identity, update and
  recovery operations, and abuse resistance before enabling remote nodes. The
  current node binds to loopback and has one validator.
- [ ] Design verifiable service rewards only after peer-to-peer validation and
  Sybil resistance exist. Do not reward self-reported uptime.
- [ ] Keep mobile payments, QR merchant checkout, deposits, withdrawals, real
  funds, and public deployment blocked on protocol, operations, security,
  privacy, and qualified legal reviews.

## Done

- [x] Choose an initial learning audience: Japanese-speaking, non-technical
  desktop testers using the local prototype.
- [x] Add Japanese/English dashboard labels and remember the language choice.
- [x] Align encrypted wallet backup formats across the browser and native
  clients and add backup interoperability checks.
- [x] Define a small local test release and record explicit exclusions.
- [x] Add isolated ledger regression coverage without opening or modifying the
  operator's `node-data` directory.
