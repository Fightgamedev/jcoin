# A beginner's guide to project agents

An AI agent is a helper that can inspect project files and, when asked, suggest
or make a focused change. Think of agents as temporary teammates: **you** still
choose the goal and review the result. They are not always running, and adding
agent profiles does not automatically make them coordinate.

JCoin includes shared project rules in [`AGENTS.md`](../AGENTS.md) and four
specialist profiles in [`.github/agents/`](../.github/agents/). GitHub Copilot
uses those profiles as reusable roles. Other coding tools may use `AGENTS.md`
as project instructions without automatically loading Copilot profiles.

## The four roles

| Role | Ask it to |
| --- | --- |
| **Coordinator** | Break down a feature, assign separate work, reconcile feedback, and review the combined change. Usually this is the main agent you are chatting with. |
| **Privacy architect** | Map what users, the validator, and network observers can learn; identify privacy requirements and trade-offs before implementation. |
| **Protocol engineer** | Implement a small, already-approved protocol or application change and describe how it works. It must not invent cryptography. |
| **Security reviewer** | Inspect a proposed change for concrete security, privacy, and correctness problems. Its Copilot profile is limited to read and search tools. |

## Your first coordinated task

1. Open the JCoin repository in your AI coding tool. Start a conversation with
   the main agent, which will act as coordinator.
2. Give it a narrow goal. If your main agent can delegate to the specialist
   profiles, ask it to do so. Otherwise, open separate chats with the privacy
   architect and security reviewer, give each the same focused context, then
   bring both reports back to the coordinator. For example:

   > Review the wallet's transaction flow. Ask the privacy architect to list
   > what information is exposed and the security reviewer to inspect the
   > relevant code. Keep both reviews read-only. Combine their findings into a
   > short report; do not change code yet.

3. Read the report. Ask questions or choose what should happen next. For
   example:

   > Make the highest-priority documentation correction from that review. Ask
   > the security reviewer to check the final diff, then summarize the result.

4. Inspect the changed files and the Git diff yourself. Ask the coordinator
   what checks it ran. A review is useful feedback, not proof that code is
   secure.
5. Only after you are comfortable with the change, ask for a commit or push.

## How to keep agents from getting in each other's way

- Give each helper a separate question or distinct files. Two agents editing
  the same file can overwrite or conflict with each other's work.
- Start with parallel, read-only reviews. Have one coordinator make edits after
  it compares those reviews.
- Ask agents to state assumptions and point to the code or documentation behind
  each finding. The coordinator should resolve disagreements rather than
  silently combine conflicting advice.
- Keep each task small. For larger work, agree on a design first, then divide
  implementation into independent pieces.
- Treat generated answers as proposals. The maintainer makes final decisions
  and checks the resulting changes.

## Using the profiles in GitHub Copilot

In a supported Copilot agent interface, open the agent picker and choose one
of the JCoin profiles. The profiles live in `.github/agents/`; commit this
folder to the repository branch you are using so Copilot can discover them.
GitHub documents how to configure repository custom agents and which Copilot
experiences support them. Availability depends on the Copilot product, IDE, and
account settings.

The `tools` lists limit what a profile can do in Copilot environments that
honor those settings. In other tools, profile text may only guide behavior and
may not technically prevent edits or commands. Always inspect the actual diff.

If your tool does not show these roles, you can still paste the role's task
from this guide into the main agent chat. In Codex, `AGENTS.md` provides shared
project instructions; ask the main agent to delegate focused reviews when
multi-agent delegation is available.

## JCoin safety rules

- The current prototype does **not** make private transactions. Sender
  addresses, recipient addresses, and amounts are visible in the ledger.
- Keeping a wallet key on your device is different from hiding payment data.
- CodeQ is not cryptography. Its current hash is not encryption.
- Never use real funds, real wallet backups, or production credentials in an
  agent prompt. Do not ask agents to expose the node to the internet.
- A future shielded-payment protocol needs an explicit threat model, established
  cryptographic components, and independent expert review before it is treated
  as secure.

## Links

- [Project overview and milestones](../README.md)
- [CodeQ design and limitations](CODEQ.md)
- [Project notes](PROJECT_NOTES.md)
- [GitHub: custom agents in Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents)
- [GitHub: custom agent configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [GitHub: using custom agents in your IDE](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-custom-agents)
