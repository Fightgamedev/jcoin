# JCoin network participation rewards

## Goal

Make it simple for someone to install JCoin on their own computer, help keep a future network available, and earn JCOIN for useful participation. The intended experience is a clear opt-in: install, see what the node contributes, see an understandable reward estimate, and pause or uninstall at any time.

This is a future design goal. The current prototype has no peer-to-peer network, no independent nodes, and no node-operator rewards. Its single local validator creates prototype block rewards for its own wallet. These rewards have no real-world value.

## Design principles

- **Reward service, not a checkbox.** A process running on a computer cannot prove its own uptime to the network. Uptime can be one eligibility signal, but rewards should depend on useful work that other participants can verify.
- **Keep participation approachable.** Offer a low-resource mode, explain storage and bandwidth needs before enabling it, and show the node's status and accrued test rewards in plain language.
- **Make rewards predictable.** Publish the issuance budget, how it changes over time, what services qualify, and how reward amounts are calculated. Do not promise income or returns.
- **Avoid rewarding duplicate identities.** The network needs a reviewed Sybil-resistance strategy so one operator cannot multiply rewards merely by creating many node identities. This may limit who can participate, so its trade-offs must be public.
- **Protect payment privacy.** Node operation must not require publishing a user's wallet balance, spending key, or payment history. Node rewards should use a separate reward key, with careful review of address reuse and network metadata leaks.
- **Fail safely.** Nodes should not spend from the operator's wallet, open inbound ports, or install updates without clear consent. Operators need a simple way to stop, upgrade, export logs, and remove local data.

## Candidate reward model to evaluate

1. A future test network defines a fixed, public reward budget per epoch.
2. Nodes perform defined tasks, such as relaying valid transactions, serving independently checked chain data, or helping verify protocol data. The protocol decides which tasks are actually useful; simply staying online is not enough.
3. Independent peers or protocol records attest to those tasks. Reward accounting applies published limits so one identity, region, or operator cannot trivially dominate the budget.
4. Rewards are provisional until the network accepts the accounting record. The wallet displays the rule and evidence behind each reward.
5. Start with valueless test tokens on a test network. Do not enable main-network issuance until the design has attack analysis, privacy review, independent implementation review, and an explicit monetary-policy decision.

This is a design sketch, not a selected consensus or proof-of-service protocol. Attestations, peer sampling, resource requirements, reward splitting, and Sybil resistance all need research and adversarial review. A reward scheme can create new privacy leaks (such as linking a node identity to a wallet) and centralization pressure; those risks are part of the design, not details to defer.

## Decisions needed before implementation

- Which node tasks improve availability and security, and how can independent parties verify them?
- What threat model covers fake peers, colluding operators, intermittent service, and identity farming?
- How does the mechanism avoid preferring always-on data centers over ordinary home computers?
- What are the total supply, per-epoch budget, adjustment rules, and treatment of missed or disputed rewards?
- Can the reward key remain separate from payment keys, and what network metadata can still link them?
- What storage, bandwidth, CPU, and electricity costs will participation require on common devices?
- What are the operator's shutdown, upgrade, recovery, and abuse-reporting controls?

## Delivery stages

1. Document and review threat model, service definitions, issuance bounds, and privacy implications.
2. Build a local simulator that compares honest home nodes with duplicate identities, collusion, and intermittent service. No real token issuance.
3. Run an opt-in test network with clearly valueless test rewards and public monitoring.
4. Commission independent security, privacy, economic, and operational review; publish findings and address them.
5. Consider a production decision only after these gates and applicable legal review. Participation rewards remain disabled until then.

## Current implementation status

The local node is not a participant in a public network. There is no node discovery, remote consensus, uptime measurement, service attestation, reward claim, or payout to other computers. Do not advertise current JCOIN block issuance as an operator reward program.
