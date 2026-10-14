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

Claude connection support is **planned**. This release registers a native Codex OAuth client only. The Claude plugin package remains available, but do not use the retired personal-token setup against updated Strato workspaces. Use [Codex guided setup](codex-guided-setup.md) for a supported connection.

The remaining skill and update instructions describe the plugin package; runtime validation in Claude remains deferred.

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
| Strato will not connect                 | Claude OAuth connection support is planned; use Codex for supported access. |
| Project server awaits approval          | Approve the Strato entry when Claude Code asks to load the project's MCP configuration.            |
| Reviews work but authoring does not     | Claude runtime support is deferred.              |
| The same skill appears twice            | See [duplicate installations](reference.md#duplicate-skills).                                      |
