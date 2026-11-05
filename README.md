# Strato agent plugins

Work with your Strato Design History File from Codex, Claude, or Claude Code. Maintained by **Stratoware LLC**.

| Skill | Purpose |
| --- | --- |
| `/strato` | Find, explain, create, update, or link DHF records. Add your direction when invoking it. |
| `/strato-design-sync` | Establish a Strato baseline or reconcile the repo and Strato specifications and designs in both directions. |
| `/strato-verification-sync` | Establish or reconcile tests, procedures, and Strato Test Cases; optionally prepare GitHub result reporting. |

## Get started

| Codex                               | Claude Code                                     |
| ----------------------------------- | ----------------------------------------------- |
| [**Set up Codex →**](docs/codex.md) | [**Set up Claude Code →**](docs/claude-code.md) |

For **Claude web, Claude Desktop, or Cowork**, connect from Strato Settings → Connectors, then [add the Strato repository marketplace](docs/claude-skills.md). The connector and skills are installed separately.

Codex supports guided installation and native OAuth. Claude Code plugin packaging is retained; Claude Code connection support is planned.

For guided Codex installation on macOS and Linux with an OS credential store, start in Strato **Profile → Connectors → Open Codex**. [Approve access in your browser](docs/codex-guided-setup.md), then restart Codex to use the connection.

You need a Strato account with MCP access. Claude Code connection support is planned.

The public repository contains release snapshots. Development history is maintained separately.

## What to expect

1. Invoke **Strato** with a direction, or choose a dedicated sync skill for a systematic comparison.
2. Work through the sync skill's questions in chat and review the proposed plan. On first sync, this includes improving existing Strato records and structure where needed.
3. Confirm the plan to apply it, or request a specific edit directly. Strato changes follow your permissions and normal review process.

Sync skills inspect the current folder and available Strato records and present findings in chat. Confirmed Strato changes are summarized in `.strato/sync-history.json`. Verification sync does not execute tests or write Test Runs.

## More information

- **Update:** [Plugin distribution and updates](docs/plugin-distribution.md)
- **Troubleshoot:** [Codex](docs/codex.md#5-troubleshoot) · [Claude Code](docs/claude-code.md#5-troubleshoot)
- [Release notes](CHANGELOG.md) · [Advanced setup and technical reference](docs/reference.md)
- [Support and contributions](CONTRIBUTING.md) · [Security reporting](SECURITY.md)
- [MIT license](LICENSE) · Copyright © 2026 Stratoware LLC
