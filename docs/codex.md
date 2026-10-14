# Get started with Codex

[← Overview](../README.md) · [Claude Code guide](claude-code.md)

You need a Strato account, Codex 0.160.0 or later on macOS or Linux, and an unlocked OS credential store.

## 1. Install the plugin

In Strato, open **Profile → Connectors → Open Codex** and send the prepared setup request. Codex installs the plugin for you. See [guided setup](codex-guided-setup.md) for details and recovery.

## 2. Connect Strato

Approve access in the Strato browser page that Codex opens. Sign in if needed, check the workspace and user, and choose read-only or read-and-write DHF access. Codex stores and renews credentials automatically.

Restart Codex if prompted, then ask: **“List the Strato products I can access using MCP.”** A successful tool request changes the Strato connection status from **Authorized** to **Connected**. Manage permissions, expiry, and Disconnect in **Profile → Connectors**.

## 3. Use Strato

Open your engineering project in Codex. Type `/`, filter with `strato`, and select **Strato**. Add what you want it to do, such as “show the requirements for this product.” See the [slash command menu](https://learn.chatgpt.com/docs/reference/slash-commands).

You can also type:

```text
Use $strato to update the architecture for this product to reflect the new acquisition service.
```

Select **Strato Design Sync** or **Strato Verification Sync** from the same slash menu, or type `$strato-design-sync` or `$strato-verification-sync`. These establish or reconcile designs and verification coverage with Strato. Work through open questions in chat, then confirm the proposed plan. All three skills summarize confirmed Strato changes in `.strato/sync-history.json`.

## 4. Update the plugin

Run in a terminal:

```bash
codex plugin marketplace upgrade strato
codex plugin add strato@strato
```

This refreshes the `stable` catalog and reinstalls from it. Start a new task afterward. Updates are manual in this guide.

Check the [release notes](../CHANGELOG.md). For pinned releases or local installations, see [advanced setup](reference.md#installation-options).

## 5. Troubleshoot

| Problem                                 | What to check                                                                                                                             |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Installation cannot find the repository | Check the repository name and your network access to GitHub.                                                                              |
| Skills do not appear                    | Confirm the plugin is installed and enabled, then start a new task or restart Codex. Workspace plugin policies may restrict availability. |
| Strato will not connect                 | Check the connection status in Strato; reconnect if expired or disconnected.                                          |
| Reviews work but authoring does not     | Check the connection’s granted permissions and the server capabilities reported by the skill.                                                     |
| The same skill appears twice            | See [duplicate installations](reference.md#duplicate-skills).                                                                             |
