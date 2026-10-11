# JCoin privacy threat model — initial draft

**Status:** design input only. This document describes the current prototype and
sets questions and requirements for future research. It is not a protocol
specification, security review, or claim that JCoin provides private payments.

## Scope and assumptions

This model covers the current local wallet-to-node transfer flow and the
privacy goals for a possible future payment protocol. JCoin is an experimental,
single-validator prototype. The node binds to `127.0.0.1:8765`
([`jcoin_node.py`](../jcoin_node.py#L19-L25)); the project does not support a
public network or real funds ([`README.md`](../README.md#L43-L64)). This
loopback restriction limits remote reachability in the current setup, but does
not make transaction data confidential from the node operator, local software,
or anyone who obtains the node's files.

The intended future goal is privacy for everyday payments, with useful
recipient confirmation and optional, limited disclosure. That goal does not
presuppose a specific protocol. This draft does not select cryptographic
primitives or claim that CodeQ contributes cryptographic security.

## Current implementation facts

- A transfer contains `amount`, `from`, `nonce`, `pub`, `time`, and `to`; the
  node validates and verifies a signature over these fields
  ([`jcoin_node.py`](../jcoin_node.py#L76-L78),
  [`jcoin_node.py`](../jcoin_node.py#L104-L130)). **Sender address, recipient
  address, and amount are cleartext. No cryptographic transaction privacy is
  implemented.**
- Pending transfers are stored as serialized transaction bodies in SQLite;
  confirmed transfers are embedded in serialized block bodies
  ([`jcoin_node.py`](../jcoin_node.py#L68-L73),
  [`jcoin_node.py`](../jcoin_node.py#L200-L225)). Anyone with access to this
  database or a process reading it can inspect the transaction details. The
  current node binds to loopback and is not a publicly reachable ledger; this
  data is visible to its operator and local software with access to the files.
- The node's `/api/pending` endpoint returns full pending transaction objects
  after its loopback and Origin check. This is a local browser-origin gate, not
  general authentication.
  `/api/blocks` returns block metadata and a transfer count, not the confirmed
  transaction bodies ([`jcoin_node.py`](../jcoin_node.py#L294-L310)). Thus,
  confirmed transfer bodies are available in local node storage, but the
  current HTTP API does not expose the whole confirmed history.
- The balance endpoint accepts an address and returns its balance, available
  amount, pending incoming amount, and nonce
  ([`jcoin_node.py`](../jcoin_node.py#L189-L197),
  [`jcoin_node.py`](../jcoin_node.py#L289-L293)). This allows anyone who can
  query the local endpoint to ask about a known address.
- Balance requests put the wallet address in the query string. The node now
  omits query strings from request-line logs, but the address still travels in
  the HTTP request and could be logged by other software or a future proxy.
- The API sends wildcard CORS headers. Browser access to loopback varies by
  browser and request context, but if cross-origin requests are permitted, an
  unrelated web page may read `/api/status`, `/api/balance`, and `/api/blocks`
  summaries. The `local_operator` check rejects untrusted browser Origins on
  `/api/pending`, `/api/master/send`, and `/api/validate`. It is not a general
  authentication system: local software or requests without an Origin header
  can still fetch full pending bodies. Consider removing the unused route or
  using a least-privilege API before handling anything sensitive.
- The browser dashboard builds a transfer with visible sender, recipient, and
  amount fields and signs it with Ed25519
  ([`dashboard.html`](../dashboard.html#L63-L76)). Its warning accurately says
  these fields are stored in cleartext and visible to the node operator
  ([`dashboard.html`](../dashboard.html#L8)). The native wallet likewise sends
  the visible fields ([`jcoin_wallet.py`](../jcoin_wallet.py#L92-L100)).
- CodeQ's standalone compiler requires plaintext recipient addresses and
  amounts and returns allocations plus an ordinary SHA-256 `intent_hash`
  ([`jcoin_codeq.py`](../jcoin_codeq.py#L57-L83),
  [`jcoin_codeq.py`](../jcoin_codeq.py#L99-L120)). It is not connected to
  transaction settlement and does not hide the intent.
- The native wallet encrypts its local private key file, but that protects key
  storage only; it does not conceal payments from the node
  ([`jcoin_wallet.py`](../jcoin_wallet.py#L60-L71)). Browser key storage is in
  IndexedDB ([`dashboard.html`](../dashboard.html#L25-L26)). Neither fact
  changes ledger transparency.

## Assets and sensitive information

1. **Payment details:** sender and recipient addresses, amounts, timing,
   transaction relationships, balances, and payment frequency.
2. **Spending authority:** wallet private keys and any future recovery material.
3. **Viewing and disclosure authority:** any future viewing keys, receipts, or
   selective-disclosure credentials.
4. **Intent and application data:** CodeQ lanes, weights, memo, expiry, and
   allocation output.
5. **Network metadata:** source and destination IP addresses, request timing,
   message sizes, and connections between wallet activity and node requests.
6. **Local records:** wallet files, browser storage, node database, logs,
   backups, and device notifications or clipboard contents.

## Actors and adversaries

- **Payer and recipient:** honest users who need to verify payment status and
  retain control of their own keys and disclosures.
- **Validator/node operator:** currently one operator who validates transfers
  and controls block production. The operator can read pending transaction
  bodies and the local database. Future privacy must state explicitly whether
  the validator is trusted with transaction details.
- **Local observer:** another process or person with access to the computer,
  database, browser profile, backups, or logs.
- **Malicious or compromised wallet software/device:** can capture keys,
  payment intents, plaintext before encryption, or recipient information.
- **Network observer or infrastructure provider:** relevant if the system ever
  uses remote nodes or a public network. Such an observer may correlate timing,
  IP address, request size, and transaction submission even if ledger fields
  are hidden.
- **Ledger/API observer:** a party able to read current node storage or query
  available endpoints. The current node is loopback-only, but anyone with
  local file access can read its SQLite data. In a future public network,
  assume ledger data is copied and retained indefinitely by observers.
- **Colluding observers:** validator, wallet service, recipient, and network
  observers may combine records. The future design must define which
  combinations it intends to resist.

## Privacy and security goals for future design

These are requirements to investigate, not current capabilities:

1. **On-ledger confidentiality:** default transactions should not reveal the
   payer, recipient, or value to ordinary ledger observers, while protocol
   validation still prevents invalid issuance, overspending, and replay.
2. **Validator privacy boundary:** define whether a validator can learn
   transaction details. Prefer a design where validating correctness does not
   require routine access to plaintext payment data; document any unavoidable
   leakage.
3. **Relationship unlinkability:** state what observers can infer across
   payments, address reuse, change, fees, and timing. Hiding individual fields
   alone is not enough if transaction relationships remain obvious.
4. **Network metadata:** separately assess IP and timing correlation, peer
   discovery, request sizes, remote node trust, and traffic-analysis limits.
   Ledger privacy must not be described as network anonymity.
5. **Wallet and recovery safety:** protect spending keys at rest and in use;
   specify recovery, backups, device compromise, loss, and migration before
   promising usable private payments.
6. **Recipient verification and receipts:** let recipients verify payment
   completion without publishing a reusable public trail. Define receipt
   authenticity, replay handling, and accidental disclosure risks.
7. **Selective disclosure:** make scope, recipient, expiry, and revocation (if
   possible) of disclosures explicit. A viewing or audit capability must not
   silently become universal surveillance access.
8. **CodeQ constraints:** define a small, deterministic language whose
   statements can be checked as part of transaction validity. Any privacy
   proof system must enforce the same rules as the wallet and validator. CodeQ
   syntax, hashes, and arithmetic alone are not privacy mechanisms.
9. **Fail safely:** reject malformed or invalid transactions without leaking
   secret witness data through errors, logs, APIs, or timing beyond the
   documented threat model.
10. **Reviewability:** use established, maintained cryptographic
    implementations and a documented threat model. Require independent
    cryptographic and implementation review before any claim of privacy or
    handling of real value.

## Risks outside this draft's protection claims

- This document does not mitigate current cleartext transaction exposure,
  wallet malware, a compromised operating system, key theft, coercion, or
  observation of a user's physical activity.
- A future shielded ledger would not by itself hide IP addresses, timing,
  device identifiers, payment requests shown to a merchant, wallet backups, or
  data disclosed by a recipient.
- A dishonest validator may censor or delay transfers, lie about confirmation,
  or control the current chain. Privacy properties do not provide decentralized
  consensus or availability.
- Amount ranges, fees, rare payment patterns, small anonymity sets, address
  reuse, and public merchant interactions can enable inference even if some
  fields are cryptographically hidden.
- No conclusions are made here about legal compliance, operational security,
  economic safety, or production readiness.

## Unresolved decisions

Resolve these with the maintainer and independent protocol experts before
implementation:

1. Which established privacy protocol and maintained implementation should be
   evaluated, and what threat model and trust assumptions does it provide?
2. Is privacy mandatory for every payment, including fees, issuance, and
   merchant receipts? What, if anything, may be transparent by explicit user
   choice?
3. Which parties should be able to learn transaction details: payer,
   recipient, validator, wallet provider, auditor, or nobody else? Are viewing
   keys needed, and what is their scope?
4. What is the intended anonymity set and expected behavior when usage is
   sparse? How are timing, batching, change, and transaction sizes handled?
5. What is the recovery model across browser and native clients? Can a user
   restore spending and viewing authority without weakening privacy?
6. How should CodeQ intents, expiry, memo, weights, and deterministic rounding
   be represented and validated privately? Which fields may be revealed to
   recipients?
7. What metadata is acceptable to expose for fees, anti-spam controls,
   issuance, refunds, and merchant accounting?
8. What implementation, audit, usability, and operational evidence is required
   before testing with users, and what is the explicit stop/go review gate?

## Change control

Treat this threat model as a living draft. Update it when data flows, APIs,
wallet storage, networking, or protocol assumptions change. No implementation
should be described as private until its properties, leakage, assumptions, and
independent review are documented against this model.
