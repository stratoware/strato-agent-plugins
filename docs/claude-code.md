# Get started with Claude Code

[← Overview](../README.md) · [Codex guide](codex.md)

You need a Strato account and Claude Code with plugin support. **Claude Code runtime testing is still pending.** These instructions follow its documented plugin and MCP interfaces.

## 1. Install the plugin

Run inside Claude Code:

```text
/plugin marketplace add stratoware/strato-agent-plugins@stable
/plugin install strato@strato
```

Start a new session after installation. See [Claude Code plugin installation](https://code.claude.com/docs/en/discover-plugins).

## 2. Connect Strato

The plugin needs an MCP connection to your Strato tenant. If you already have one, keep it and add the tool permission below. A connection configured in Codex does not configure Claude Code.

[Create a Strato access token →](strato-token.md)

Make the token available to Claude Code as `STRATO_MCP_TOKEN`. In your engineering project's `.mcp.json`, merge this entry into `mcpServers`, preserving existing servers:

```json
{
  "mcpServers": {
    "strato": {
      "type": "http",
      "url": "https://YOUR-TENANT.stratoware.io/api/mcp",
      "headers": {
        "Authorization": "Bearer ${STRATO_MCP_TOKEN}"
      }
    }
  }
}
```

Replace `YOUR-TENANT` with your Strato subdomain. Keep the literal `${STRATO_MCP_TOKEN}` placeholder; Claude Code reads its value from the environment. Do not put the token itself in this file or in chat.

Merge this permission into the project's `.claude/settings.json`, preserving existing settings and entries in `permissions.allow`:

```json
{
  "permissions": {
    "allow": ["mcp__strato__*"]
  }
}
```

This automatically approves Strato's read and write tool calls. To apply the permission across your projects, use `~/.claude/settings.json` instead. See [Claude Code tool permissions](https://code.claude.com/docs/en/permissions).

Start Claude Code in that project with the variable available. Approve the project MCP connection when prompted. Run `/mcp` to check its status, then ask: **“List the Strato products I can access using MCP.”** See [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp).

## 3. Use Strato

Invoke Strato with a direction in your engineering project:

```text
/strato:strato show the requirements for this product
```

To reconcile designs or verification coverage with Strato, use one of the sync workflows:

```text
/strato:strato-design-sync
```

```text
/strato:strato-verification-sync
```

Add a product name or scope if needed. Work through open questions in chat, then confirm the proposed plan. All three skills summarize confirmed Strato changes in `.strato/sync-history.json`.

## 4. Update the plugin

Run inside Claude Code:

```text
/plugin marketplace update strato
/plugin update strato@strato
```

Start a new session afterward. Check the [release notes](../CHANGELOG.md). Third-party marketplace auto-updates are disabled by default; you can manage them through `/plugin` → **Marketplaces**. See [Claude Code updates](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates).

For pinned releases or local installations, see [advanced setup](reference.md#installation-options).

## 5. Troubleshoot

| Problem                                 | What to check                                                                                      |
| --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Installation cannot find the repository | Check the repository name and your network access to GitHub.                                      |
| Skills do not appear                    | Check that `strato@strato` is installed and enabled in `/plugin`, then start a new session.        |
| Strato will not connect                 | Check `/mcp`, the tenant URL, token validity, and whether Claude Code received `STRATO_MCP_TOKEN`. |
| Project server awaits approval          | Approve the Strato entry when Claude Code asks to load the project's MCP configuration.            |
| Reviews work but authoring does not     | Check the token's write permission and the server capabilities reported by the skill.              |
| The same skill appears twice            | See [duplicate installations](reference.md#duplicate-skills).                                      |
