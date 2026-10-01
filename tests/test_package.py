from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_both_clients_resolve_the_same_plugin_and_release() -> None:
    codex_catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    claude_catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    codex_plugin = ROOT / codex_catalog["plugins"][0]["source"]["path"]
    claude_plugin = ROOT / claude_catalog["plugins"][0]["source"]
    assert codex_plugin.resolve() == claude_plugin.resolve()
    codex = json.loads((codex_plugin / ".codex-plugin/plugin.json").read_text())
    claude = json.loads((claude_plugin / ".claude-plugin/plugin.json").read_text())
    for field in ("name", "version", "author", "description", "license"):
        assert codex[field] == claude[field]
    assert codex["license"] == "MIT"
    assert (codex_plugin / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    assert f"## {codex['version']}\n" in (ROOT / "CHANGELOG.md").read_text()
    assert codex["interface"]["developerName"] == claude["author"]["name"]
    for name in ("strato", "strato-design-sync", "strato-verification-sync"):
        assert (codex_plugin / "skills" / name / "SKILL.md").is_file()
