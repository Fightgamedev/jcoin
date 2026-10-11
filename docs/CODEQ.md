# Jcoin CodeQ concept

**CodeQ** means **Conserved-Quanta Payment Code** in this project. The long-term
goal is a privacy-first payment-intent language: a wallet describes the
intended payment and a proof verifies that the rules were followed without
publishing the sender, recipients, or amounts. CodeQ should be declarative,
strongly typed, and limited to auditable payment rules; it must never execute
arbitrary user code.

The current implementation is only an arithmetic spike. It computes
multi-recipient allocations in plain text and publishes an ordinary SHA-256
hash of that plain text. That hash can detect edits but **does not hide or
encrypt** the intent. Do not put private payment details into a CodeQ object
that could be shared or recorded publicly.

CodeQ is a Jcoin project term. The name is already used by unrelated software
projects, so it should not be treated as unique branding or a cleared product
name. No claim is made that the math or payment idea is unprecedented.

## The Q-conservation rule (transparent prototype)

Jcoin currently counts whole JCOIN, so one `q` quantum is one JCOIN in this
prototype. An intent has a total amount `A` and lanes with integer weights `wᵢ` in
basis points. The weights must sum to `W = 10,000`.

For every lane, first calculate:

```text
baseᵢ      = floor(A × wᵢ / W)
remainderᵢ = (A × wᵢ) mod W
```

Any quanta left after the base allocations are assigned, one each, to lanes in
descending remainder order. Equal remainders use the SHA-256 order of the
intent ID, lane ID, and destination. This makes the split deterministic and
enforces the invariant:

```text
sum(allocationᵢ) = A
```

No fractional coins are created or lost, and the validator does not choose who
gets a rounding unit. This is an application-specific use of integer
apportionment and hashing, not a claim of new foundational mathematics. The
output currently contains the amount, every recipient, every allocation, and a
non-hiding `intent_hash`.

## Prototype

`jcoin_codeq.py` compiles a declarative intent into cleartext allocations and a
SHA-256 `intent_hash`. It accepts no executable scripts. Run the local example
with:

```sh
python3 jcoin_codeq.py
```

The compiler checks the amount, expiry, recipients, unique lanes, and exact
weight sum. `verify_codeq` recompiles a result and checks that its allocations
and hash match the intent. Neither function provides transaction privacy.

## Example intent

```json
{
  "id": "cafe-order-001",
  "amount": 101,
  "expires_at": 2000000000,
  "memo": "Cafe order",
  "lanes": [
    {"id": "merchant", "to": "JC…", "weight_bps": 9000},
    {"id": "savings", "to": "JC…", "weight_bps": 1000}
  ]
}
```

## Privacy-first protocol direction

The proposed direction is a **shielded note pool** with privacy on by default.
Each payment would create hidden-value notes represented on the public ledger
by hiding commitments. The sender would reveal a unique nullifier when
spending a note; a zero-knowledge proof would show that the note exists, is
unspent, and that input value equals output value plus any public fee. CodeQ's
allocation rule would be checked inside that proof, while note contents and
recipient data are encrypted for their owners. Wallet-controlled viewing keys
and payment proofs could disclose selected details to a recipient or auditor.

This is a design direction, not an implemented protocol. A maintained,
independently reviewed proving system and audited cryptographic primitives
must be selected before implementation. CodeQ can specify constraints and
compile them into a proof circuit; a new syntax or custom math alone cannot
make the system more secure. Privacy claims must include network metadata,
wallet storage, backups, and validator visibility, not only public-chain data.

## Not connected to funds yet

This is a math and serialization prototype only. It does not hide data, create
wallet transactions, check recipient consent, prevent replay, escrow funds, or
enforce merchant refunds. Before integrating it with the node, the protocol
needs a versioned signed-intent format, shielded inputs and outputs,
double-spend prevention, explicit cancellation and expiry behavior, and
independent cryptographic review. For now it must not be presented as a private
or working payment feature.

Prior-art and naming research is incomplete. Treat CodeQ as an experiment, not
as a claim of novelty, security, or affiliation with any existing CodeQ project.
