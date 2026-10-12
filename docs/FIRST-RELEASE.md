# First release scope

**Status:** working product direction for the local test prototype. This is not
a public launch plan, support promise, or financial product specification.

## First audience

Start with Japanese-speaking, non-technical testers who can run the local
prototype on a desktop computer. This is a practical learning audience for
the current single-machine node: the project cannot yet serve remote users or
phone-only users. Make the wallet's core tasks understandable without asking
testers to understand validators, cryptography, or CodeQ.

The longer-term product goal remains straightforward everyday payments in
Japan. Do not imply that JCoin is affiliated with PayPay or any other payment
provider. A mobile, remotely accessible product is a later phase, after a
reviewed network and privacy design exist.

## First useful test release

The test release should let one person, on the local prototype:

1. Create a wallet and save an encrypted backup, or restore one.
2. See and copy the wallet address; request a small amount of valueless test
   coins from the local faucet.
3. See a clear test balance and each transfer's pending, confirmed, or rejected
   state.
4. Choose transparent test sending only after a plain-language disclosure;
   private mode stays selected by default and must fail closed.
5. See whether a transfer is waiting, confirmed, or rejected, with a useful
   next step for each state.

## Out of scope for this release

- Real money, exchange rates, deposits, withdrawals, or claims of monetary
  value.
- Remote access, mobile-only use, merchant checkout, or production support.
- Private transfers: no reviewed shielded protocol is implemented.
- Public consensus, peer discovery, third-party node rewards, or tokenomics
  promises.
- Custom cryptographic constructions presented as novel or secure.

## Implementation order and acceptance

1. Keep backup creation, recovery, wrong-password handling, and cross-client
   format checks reliable. **Current automated backup checks are in place.**
2. [x] Improve the dashboard's first-run, receive, and backup instructions
   for the selected Japanese-speaking test audience; provide Japanese and
   English labels with a remembered language choice.
3. Add clear transfer lifecycle feedback using only states the node can
   actually verify; do not label a queued transfer as paid or confirmed.
4. Keep transparent sends visibly marked as test-only, with explicit consent
   before submission. Do not silently fall back from private mode.
5. Before inviting testers, document setup, reset/recovery, known data
   exposure, and how to report a problem. Keep testing local and use test
   coins.

The first release is useful when a new tester can create or restore a wallet,
copy a receive address, complete an explicitly transparent test transfer,
and correctly tell whether it is pending or confirmed, without mistaking the
prototype for a private or production payment system.

## Decisions still required before protocol work

This scope does not answer whether privacy is mandatory for every transaction,
what selective disclosure should exist, or which established protocol is
appropriate. Keep those questions open in the [privacy threat model](PRIVACY-THREAT-MODEL.md)
and [protocol evaluation](PRIVACY-PROTOCOL-EVALUATION.md); require expert
review before implementation.
