# JCoin Explicit Privacy Protocol (working title)

**Status:** research proposal only. This is not implemented, cryptographically
specified, novel-prior-art-cleared, or safe for funds. The wallet currently
supports transparent test transfers only.

## Goal

Give every payment one explicit visibility mode. **Private is the wallet
default.** A user may deliberately choose a transparent payment when they
accept that the sender, recipient, amount, and transaction relationship will
be public. A private payment must never silently become transparent because
of an unsupported wallet, recipient, node, or error.

The working idea is a *mode-locked payment intent*: the visibility choice is
part of the signed intent and cannot be changed by a relay, validator, or
automatic fallback. This is an application protocol and UX rule, not a new
cryptographic primitive. The name is provisional and no claim is made that the
composition is unprecedented.

## Transaction modes

### Private (default)

- The wallet creates a shielded payment using a selected, maintained, reviewed
  privacy protocol implementation. JCoin does not yet have one selected.
- The ledger validates the required value-conservation, authorization,
  double-spend, and CodeQ rules through that implementation without exposing
  sender, recipient, or amount to ordinary ledger observers.
- Only the recipient and parties the wallet holder deliberately authorizes
  can inspect the payment details, subject to the selected protocol's actual
  viewing-key and receipt semantics.
- The mode is fail-closed: if the recipient, node, or chain cannot handle the
  private transfer, the wallet rejects it and explains why. It never retries
  as transparent.

This mode cannot be implemented by encrypting the current JSON fields or
adding a `private: true` flag. It needs shielded notes or an equivalent
established protocol, proof verification, wallet scanning and recovery,
consensus rules, and a complete review. A shielded ledger also does not
automatically hide IP addresses, timing, traffic volume, or recipient-device
data.

### Transparent (explicit opt-in)

- The wallet warns the user before submission that sender, recipient, amount,
  and timing are visible to the node and anyone able to inspect its ledger.
- The user confirms the exact recipient and amount. The wallet records the
  transparent mode in the signed transaction format once such a format is
  designed.
- There is no conversion from a private payment to a transparent payment. To
  send transparently, the user must select that mode and confirm it.

The current local prototype only implements this mode. Its current transaction
format does not contain a privacy-mode field; the dashboard's mode selector
is therefore only a safe UX preview and must not be interpreted as a protocol
implementation.

## Mode-lock invariant

For a future versioned transaction format, the user's intent must commit to
the selected mode before transaction construction. The verifier must reject a
transaction whose encoded mode, proof type, or visible fields conflict. A
private transaction cannot carry plaintext payment fields as a hidden
fallback; a transparent transaction cannot claim shielded status. Unsupported
mode, failed proof, stale wallet, or unavailable recipient support must fail
without mode conversion.

The mode itself may be public metadata. The protocol must assess whether even
that bit, combined with timing, size, or repeated use, leaks sensitive
information.

## CodeQ and payment receipts

If CodeQ is retained, its exact bounded semantics must be committed to and
verified as part of the selected transaction protocol. The proof must bind the
intent to the actual outputs and define amount conservation, recipient
authorization, expiry, rounding, cancellation, and replay protection. An
ordinary hash or wallet-side calculation is insufficient. Transparent mode
may show CodeQ fields publicly; private mode must prove the same rules without
publishing private lane data. Receipt and viewing-key disclosure must be
separately authorized and scoped.

## Wallet experience requirements

1. Start each new send in **Private (recommended)** mode.
2. Explain plainly when private mode is not yet supported; never imply privacy
   from the selected option alone.
3. Put **Transparent test payment** behind an intentional mode switch and a
   per-send disclosure confirmation.
4. Show the exact details that will be public before final confirmation.
5. Do not remember transparent mode as the default for the next payment or
   another wallet.
6. Reject unsupported privacy-mode transfers rather than downgrading them.
7. Clearly distinguish on-ledger privacy from network anonymity and local
   device privacy.

## Required review before implementation

- Select an established protocol and maintained implementation against the
  [privacy protocol evaluation](PRIVACY-PROTOCOL-EVALUATION.md).
- Specify transaction encoding, mode commitment, proof statements, fee and
  issuance handling, consensus checks, wallet key derivation, scanning,
  recovery, receipts, and upgrade behavior.
- Analyze failures, malicious downgrade attempts, wallet/provider leakage,
  network metadata, sparse usage, and transparent/private linkage.
- Obtain independent cryptographic and implementation review. Do not deploy
  the private mode or represent it as secure before review is complete.
- Keep all current transfers local and test-only. The existing prototype can
  only send transparent transactions.
