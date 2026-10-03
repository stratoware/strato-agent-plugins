# Get started with Codex

[← Overview](../README.md) · [Claude Code guide](claude-code.md)

You need a Strato account and a Codex version with plugin marketplace support.

## 1. Install the plugin

Run these commands in a terminal:

```bash
codex plugin marketplace add stratoware/strato-agent-plugins --ref stable
codex plugin add strato@strato
```

## 2. Connect Strato

Installing the plugin adds the skills. Set up its connection below, or update the approval setting on your existing Strato connection.

[Create a Strato access token →](strato-token.md)

Make the token available to the Codex process as the environment variable `STRATO_MCP_TOKEN`. Keep its value out of project files and chat prompts.

Add or update this entry in `~/.codex/config.toml`:

```toml
[mcp_servers.strato]
url = "https://YOUR-TENANT.stratoware.io/api/mcp"
bearer_token_env_var = "STRATO_MCP_TOKEN"
default_tools_approval_mode = "approve"
```

Replace `YOUR-TENANT` with your Strato subdomain. For example, `https://acme.stratoware.io` becomes `https://acme.stratoware.io/api/mcp`.

The `approve` setting automatically approves Strato's read and write tool calls. For a connection limited to one project, use that project's `.codex/config.toml` instead.

Restart Codex with the token available in its environment. Setting a variable in an unrelated terminal does not make it available to an already-running desktop app. See [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp).

Ask in a new task: **“List the Strato products I can access using MCP.”**

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
| Strato will not connect                 | Check the tenant URL, token validity, and whether the Codex process received `STRATO_MCP_TOKEN`.                                          |
| Reviews work but authoring does not     | Check the token's write permission and the server capabilities reported by the skill.                                                     |
| The same skill appears twice            | See [duplicate installations](reference.md#duplicate-skills).                                                                             |
