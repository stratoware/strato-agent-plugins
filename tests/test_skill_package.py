from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "plugins/strato/skills").iterdir())
MARKDOWN = sorted(
    [*ROOT.glob("*.md")]
    + [path for folder in ("docs", "plugins", "tests") for path in (ROOT / folder).rglob("*.md")]
)


@pytest.mark.parametrize("skill", SKILLS, ids=lambda path: path.name)
def test_skill_metadata_and_interface_are_loadable(skill: Path) -> None:
    content = (skill / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n(.+)", content, re.DOTALL)
    assert frontmatter, f"Missing skill frontmatter or body: {skill}"
    metadata = yaml.safe_load(frontmatter[1])
    assert metadata["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"])
    assert len(metadata["name"]) <= 64
    assert isinstance(metadata["description"], str)
    assert 0 < len(metadata["description"].strip()) <= 1024
    assert "[TODO:" not in content

    interface = yaml.safe_load((skill / "agents/openai.yaml").read_text())["interface"]
    for field in ("display_name", "short_description", "default_prompt"):
        assert isinstance(interface[field], str) and interface[field].strip()
    assert f"${skill.name}" in interface["default_prompt"]


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda path: str(path.relative_to(ROOT)))
def test_local_documentation_resources_exist(path: Path) -> None:
    parser = MarkdownIt()
    for token in parser.parse(path.read_text()):
        for child in token.children or []:
            target = child.attrGet("href") if child.type == "link_open" else child.attrGet("src")
            if not target or target.startswith("#") or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resource = (path.parent / target.split("#", 1)[0]).resolve()
            assert resource.is_relative_to(ROOT), f"Nonportable resource in {path}: {target}"
            assert resource.exists(), f"Broken resource in {path}: {target}"
