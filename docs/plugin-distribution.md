# Update the Strato plugin

The Strato plugin contains all three skills. Updating it preserves your existing Strato connection. See the [release notes](../CHANGELOG.md) for changes.

## Codex

For an existing installation, run:

```sh
codex plugin marketplace upgrade strato
codex plugin add strato@strato
```

Start a new chat afterward. For pinned releases or local installations, see [advanced setup](reference.md#installation-options).

## Claude web and Cowork

Follow [the Claude setup guide](claude-skills.md) for installation. Manage updates from the Strato marketplace in Claude's Plugins. If your organization manages the plugin, contact its owner. See [Claude's plugin instructions](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

## Claude Code

In a terminal, run:

```sh
claude plugin marketplace update strato
claude plugin update strato@strato
```

Start a new session afterward. Manage optional automatic updates through `/plugin` → **Marketplaces**. These commands update the local Claude Code installation. See [Claude Code update documentation](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated).
