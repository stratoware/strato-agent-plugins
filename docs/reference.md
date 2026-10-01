# Advanced setup and technical reference

[← Overview](../README.md) · [Codex guide](codex.md) · [Claude Code guide](claude-code.md)

## Installation options

### Local or downloaded packages

For Codex, register the distribution root:

```bash
codex plugin marketplace add /absolute/path/to/strato-agent-plugins
codex plugin add strato@strato
```

For Claude Code, run inside the client:

```text
/plugin marketplace add /absolute/path/to/strato-agent-plugins
/plugin install strato@strato
```

To update a local installation, obtain the new package and replace the source directory before reinstalling. Git marketplace refresh commands do not download a new local package.

### Pinned releases and rollback

Use an immutable release tag instead of `stable` when adding the marketplace:

| Client      | Marketplace source                             |
| ----------- | ---------------------------------------------- |
| Codex       | `stratoware/strato-agent-plugins --ref v0.2.3` |
| Claude Code | `stratoware/strato-agent-plugins@v0.2.3`       |

Refreshing a pinned tag keeps that release. To change a registered Codex marketplace to a specific release:

```bash
codex plugin marketplace remove strato
codex plugin marketplace add stratoware/strato-agent-plugins --ref v0.2.3
codex plugin add strato@strato
```

For Claude Code:

```text
/plugin marketplace remove strato
/plugin marketplace add stratoware/strato-agent-plugins@v0.2.3
/plugin install strato@strato
```

Removing a Claude Code marketplace also uninstalls its plugins. Start a new task or session after reinstalling. See [Claude Code marketplace management](https://code.claude.com/docs/en/discover-plugins#manage-marketplaces) and [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins).

Changing plugin versions does not undo Strato records, authored tests, or project mappings. Check the [release notes](../CHANGELOG.md) for compatibility. MCP server deployments are separate; reconnect or restart your client after server tool changes.

## Duplicate skills

If you previously installed the skills individually, remove those standalone installations after validating the plugin. Keep your project's `.strato` history and test mappings.

## Permissions

| Strato permission             | Scope identifier        |
| ----------------------------- | ----------------------- |
| Read DHF records              | `dhf:records:read`      |
| Write DHF development records | `dhf:development:write` |

The write scope covers Software, Hardware, and Labeling Specifications, Design Elements and their links, Test Cases, and Test Runs. Mechanical requirements use Hardware Specification records.

Although the server's write permission includes Test Runs, the verification skill does not execute tests or create, update, or complete Test Runs.

## Sync history

All three skills give answers and findings directly in chat. After applying selected Strato changes and confirming the results, they append one entry to `.strato/sync-history.json`. Each entry contains a timestamp and a short summary, for example:

```json
[
  {
    "timestamp": "2026-09-27T20:00:00Z",
    "summary": "Controller: imported the interface specifications and linked their designs."
  }
]
```

Missing or empty history means first sync. Each review compares the current repo with current Strato records, including any unfinished work. Reviews, local-only edits, and failed or unconfirmed writes do not add events. Partial completion is recorded as partial.

## Verification mappings and results

- [Test mapping schema](../plugins/strato/skills/strato-verification-sync/assets/test-mapping.schema.json) · [Example](../plugins/strato/skills/strato-verification-sync/assets/test-mapping.example.json)
- [GitHub result schema](../plugins/strato/skills/strato-verification-sync/assets/test-results.schema.json) · [Example](../plugins/strato/skills/strato-verification-sync/assets/test-results.example.json)
- [GitHub reporting reference](../plugins/strato/skills/strato-verification-sync/references/github-results.md)
- [Swift testing guidance](../plugins/strato/skills/strato-verification-sync/references/swift-testing.md) covers XCTest, Swift Testing, and existing Xcode/Swift Package Manager results. Reporting adapters still require validation against the project's toolchain.

The optional [mapping validator](../plugins/strato/skills/strato-verification-sync/scripts/validate_verification.py) requires [uv](https://docs.astral.sh/uv/) and declares its Python dependencies. GitHub access is needed only when selected work requires reading GitHub artifacts or configuring workflows. Strato's GitHub result importer is outside this plugin's scope.

## Maintaining the plugin

Both clients share the instructions and schemas in `plugins/strato/skills/`. Their manifests and MCP configurations differ. See [support and contributions](../CONTRIBUTING.md) for reporting issues and validating a downloaded release.
