# Support and contributions

Stratoware LLC maintains these plugins. The public repository distributes release snapshots; development takes place separately.

## Report a problem or suggest a change

Open a [GitHub issue](https://github.com/stratoware/strato-agent-plugins/issues) with the plugin version, client and client version, steps to reproduce, and expected and observed behavior. For suggestions, describe the workflow you want to improve.

Use a minimal example without access tokens, customer records, or confidential engineering files. Report security concerns through the [private reporting process](SECURITY.md).

Discuss proposed contributions in an issue first so we can coordinate the change and include it in a release.

## Validate a downloaded release

With [uv](https://docs.astral.sh/uv/) installed, run from the package root:

```bash
uv sync --locked
uv run --no-sync pytest -q
uv run --no-sync ruff check .
```

These checks validate package structure, documentation links, and verification data contracts. They do not connect to Strato or execute product verification tests.
