# Jcoin CodeQ concept

**CodeQ** means **Conserved-Quanta Payment Code** in this project. It is a
proposed payment-intent format for describing one payment that
can flow to multiple destinations. A buyer could approve one clearly explained
payment while the intent specifies a merchant share and optional, explicitly
chosen shares such as savings or a community fund.

CodeQ is a Jcoin project term. The name is already used by unrelated software
projects, so it should not be treated as unique branding or a cleared product
name. No claim is made that the math or payment idea is unprecedented.

## The Q-conservation rule

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
apportionment and hashing, not a claim of new foundational mathematics.

## Prototype

`jcoin_codeq.py` compiles a declarative intent into allocations and a SHA-256
commitment. It accepts no executable scripts. Run the example with:

```sh
python3 jcoin_codeq.py
```

The compiler checks the amount, expiry, recipients, unique lanes, and exact
weight sum. `verify_codeq` recompiles a result and checks that its allocations
and commitment match the intent.

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

## Not connected to funds yet

This is a math and serialization prototype only. It does not create wallet
transactions, check recipient consent, prevent replay, escrow funds, or enforce
merchant refunds. Before integrating it with the node, the protocol needs a
versioned signed-intent format, replay protection, explicit cancellation and
expiry behavior, and transaction tests. For now it must not be presented as a
working payment feature.

Prior-art and naming research is incomplete. Treat CodeQ as an experiment, not
as a claim of novelty, security, or affiliation with any existing CodeQ project.
