# JCoin improvement backlog

This backlog comes from a review of the local prototype. It separates
immediate usability and correctness work from protocol and production work.
Nothing here changes the current test-only status or promises a launch date.

## Active: make the local test flow usable

- [ ] **Implementation underway:** Give a new browser wallet an obvious way to
  request one capped 100-coin test transfer from the local node wallet. The
  node enforces one request per address; coins have no value.
- [ ] **Implementation underway:** Show pending, confirmed, and rejected
  transfers for the selected wallet, including amount, other address, time,
  and an actionable rejection reason. A queued transfer is not described as
  confirmed.
- [ ] **Implementation underway:** Preserve and report rejected queued
  transfers when a block is made instead of silently deleting them.
- [ ] Manually verify Japanese and English dashboard behavior after the recent
  language-switch change, including first-run, backup restore, privacy choice,
  and narrow-screen layout.
- [ ] Add automated coverage for wallet funding, transaction validation,
  block confirmation/rejection, and node restart/recovery. The existing suite
  covers encrypted wallet backups only.

## Correctness and local key recovery

- [ ] At startup, check transaction signatures and ledger semantics in every
  stored block: nonce order, nonnegative balances, reward schedule, and supply
  cap. Current startup checks verify block links, hashes, and validator
  signatures only.
- [ ] Document a safe backup and restore procedure for the node database and
  validator key. The validator key is stored as raw bytes protected by local
  file permissions, not encrypted at rest.
- [ ] Review concurrency and database transaction boundaries before the node
  handles anything beyond local prototype use.
- [ ] Break large HTML, CSS, JavaScript, and compressed Python functions into
  reviewable pieces without changing the protocol format accidentally.

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
