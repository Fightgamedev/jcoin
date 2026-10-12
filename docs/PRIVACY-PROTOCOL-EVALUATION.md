# Privacy protocol evaluation: decision input

**Status:** early comparison, not a protocol choice or implementation plan.
JCoin currently has no private transactions. The existing ledger and wallet
send cleartext sender addresses, recipient addresses, and amounts. See the
[privacy threat model](PRIVACY-THREAT-MODEL.md).

## Purpose

JCoin's stated goal is private everyday payments, with simple wallet flows and
CodeQ payment rules. This note compares two established privacy models to
make the design choices visible. It does not recommend copying either
protocol, and it does not establish that either one can be safely integrated
into JCoin. A cryptocurrency protocol is a complete system: transaction
format, consensus, wallet scanning and recovery, network behavior, upgrades,
and long-term maintenance all matter.

## High-level comparison

| Area | Monero model | Zcash shielded-note model | JCoin question |
| --- | --- | --- | --- |
| Recipient privacy | One-time stealth outputs are created for recipients. | Encrypted shielded notes are created for recipients. | Can a recipient use one simple receive code without creating a public address graph? |
| Sender privacy | Ring signatures make a spender's input one member of a set of possible inputs. | A shielded spend reveals a nullifier to prevent reuse while a proof establishes spend validity. | What does the public learn about inputs, and how strong is the anonymity set in ordinary use? |
| Amount privacy | RingCT hides amounts while proofs enforce value balance and range constraints. | Value commitments and zero-knowledge proofs support shielded value transfers. | Can fees, issuance, and CodeQ allocation be checked without publishing payment amounts? |
| Privacy default | Monero's core transaction privacy features are applied by default. | Zcash supports shielded and transparent pools; using transparent paths can expose information. | JCoin's requirement currently says privacy by default. Would any transparent path undermine that promise? |
| Selective disclosure | View keys support some auditing and wallet scanning use cases, with limits. | Viewing keys and unified viewing-key formats support scoped viewing workflows. | What receipt or audit capability is needed, and exactly which payments can it reveal? |
| CodeQ fit | Existing transaction rules do not automatically prove JCoin-specific CodeQ allocation semantics. | Existing shielded proofs do not automatically enforce JCoin-specific CodeQ allocation semantics. | Is CodeQ small and fixed enough to audit as a protocol constraint, without introducing an unreviewed custom proof system? |
| Integration cost | Requires the protocol's transaction, wallet, consensus, and networking model, not only its privacy primitives. | Requires note, proof, wallet, parameter/upgrades, and consensus integration, not only a shielded address. | Should JCoin adopt an existing full protocol/ecosystem, or stop and build a separate research prototype? |

The Monero documentation describes stealth addresses as one-time recipient
addresses, ring signatures as obscuring which ring member authorized a spend,
and RingCT as hiding transaction amounts. These properties work together;
they are not independent switches that can be added to the current account and
nonce ledger. [Stealth addresses](https://web.getmonero.org/resources/moneropedia/stealthaddress.html),
[ring signatures](https://web.getmonero.org/resources/moneropedia/ringsignatures.html),
[RingCT](https://web.getmonero.org/resources/moneropedia/ringCT.html).

The Zcash protocol specification describes shielded notes, revealed nullifiers
to prevent a note being spent twice, commitments for new notes, and zero-
knowledge proofs that establish transaction validity. It also specifies
transparent-to-shielded pool movement that reveals the transferred amount.
Shielding a field does not make all transaction paths or network metadata
private. [Zcash protocol specification](https://zips.z.cash/protocol/protocol.pdf).
Zcash's [Unified Addresses and Viewing Keys specification](https://zips.z.cash/zip-0316)
also illustrates the wallet-compatibility and disclosure design work needed
around a shielded protocol.

These are summaries of documented designs, not independent security
evaluations. Features, wallet support, and protocol versions evolve; any
implementation study must verify current specifications and maintained code.

## Implications for CodeQ

CodeQ must remain an application-level description of allowed payment rules;
it must not be presented as cryptography. The current prototype calculates
allocations in plaintext and publishes an ordinary SHA-256 hash. That hash
does not hide the intent.

For any future shielded implementation, the protocol must define exactly which
CodeQ fields are committed to and proved: amount conservation, lane weights,
expiry, recipient authorization, rounding, cancellation, and replay
protection. A proof must establish that the committed intent is the same one
used to create the shielded outputs. It must not rely on a wallet UI behaving
honestly.

The current tie-break uses the intent ID, lane ID, and destination. If any of
these values can be chosen or ground by a sender, they may influence which
lane receives indivisible remainder units. A protocol design must decide
whether this is acceptable, how values are canonicalized and committed, and
whether a simpler consensus rule is safer. These fields may also leak
information if published outside the shielded proof.

Do not add custom cryptographic primitives or an ad hoc proof circuit to make
CodeQ fit a preferred design. First define a bounded language and prove that
its semantics can be encoded consistently in the selected, reviewed system.

## Decision criteria

Before selecting a path, document and review:

1. **Adversary and trust:** what can ledger observers, validators, wallet
   providers, recipients, colluding parties, and network observers learn?
2. **Privacy defaults and leakage:** sender, recipient, amount, timing,
   transaction size, fee, issuance, pool crossings, and transaction
   relationships.
3. **Correctness:** conservation, valid issuance, double-spend prevention,
   replay resistance, and consensus behavior under malformed or adversarial
   inputs.
4. **Anonymity in practice:** the effective anonymity set, usage patterns,
   sparse-network behavior, and effects of address reuse or rare CodeQ flows.
5. **Disclosure and recovery:** recipient confirmation, backup/restore,
   viewing keys, receipts, lost devices, and limits on audit access.
6. **Implementation evidence:** maintained code, compatible libraries,
   upgrade process, independent audits, proving/verifying costs, and wallet
   support across the project's target devices.
7. **Operational privacy:** remote-node trust, peer discovery, IP and timing
   correlation, logging, backups, and node rewards that could associate a
   network identity with a payment identity.
8. **Project fit:** whether the required consensus, fees, issuance, and
   community ecosystem can be adopted without creating a brittle hybrid or
   implying that a small prototype is secure enough for real funds.

## Current conclusion and next gate

**No protocol is selected.** The current single-validator account/nonce
prototype is not a suitable base for claiming Monero-like or Zcash-like
privacy. Adding a hidden amount field or encrypting the current transaction
JSON would not supply a complete private-payment protocol.

The next gate is a maintained-implementation and architecture study against
the criteria above. It should answer whether the project should (a) build on
an existing protocol and ecosystem, (b) maintain a separate experimental
network using an established implementation, or (c) defer custom protocol
work. A custom design should proceed only with qualified cryptographic
expertise, an explicit threat model, and independent review. Until that gate
is complete, keep JCoin local and test-only, and make no claim that payments
are private.
