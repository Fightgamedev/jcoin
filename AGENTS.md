# Working with agents on JCoin

This file gives coding agents shared project context. Read it before making
changes; the human maintainer decides priorities and approves product or
protocol decisions.

## Project facts

- JCoin is an experimental, single-validator prototype. The current ledger is
  transparent and exposes sender addresses, recipient addresses, and amounts.
- Transaction privacy is a core goal, not an implemented feature. Never imply
  the current wallet or ledger provides private payments.
- CodeQ is an experimental declarative payment-rule idea. Its current
  allocation compiler and SHA-256 intent hash do not provide privacy or new
  cryptographic security.
- No real funds, public network, or production deployment are supported.

## Shared working rules

1. Start by reading the relevant README and `docs/PROJECT_NOTES.md`. Check the
   working tree before editing and preserve unrelated user changes.
2. The coordinating agent owns the task plan, resolves conflicts, integrates
   work, and reports the final result. Give each helper a small, distinct
   deliverable and name the files it may change.
3. Do not have two agents edit the same file at the same time. Prefer read-only
   review tasks for parallel helpers. The coordinator reviews every suggestion
   and owns integration.
4. Do not invent cryptographic primitives, claim novelty, or implement a
   shielded protocol from an unreviewed design. Use established libraries and
   require a written threat model and expert review for privacy-protocol work.
5. Keep the prototype local-only. Never add real credentials, wallet keys,
   private backups, generated node data, real funds, or instructions to expose
   the node to the internet.
6. Make the smallest coherent change. Keep user-facing statements consistent
   with what the code actually does, and update the relevant documentation.
7. Report what changed, decisions or risks that need human review, and what
   verification was performed. Do not claim checks that were not run.

## Coordination handoff

When asking another agent for help, include:

- the goal and relevant context;
- the exact question or deliverable;
- files to inspect or edit (and files not to edit);
- constraints, especially the current privacy limitations;
- the expected response: findings, proposed patch, or review notes.

The coordinator should compare findings, resolve disagreements explicitly,
inspect the final diff, and summarize any decisions that still need the human
maintainer.
