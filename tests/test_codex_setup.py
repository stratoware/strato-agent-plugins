from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import tomlkit

SETUP = Path(__file__).resolve().parents[1] / "plugins/strato/setup"
sys.path.insert(0, str(SETUP))

import configuration  # noqa: E402
import credentials  # noqa: E402
import workspace  # noqa: E402

ORIGIN = "https://acme.stratoware.io"
TOKEN = "pqmcp_00000000-0000-4000-8000-000000000001_" + "x" * 43


@pytest.mark.parametrize(
    "url",
    [
        "http://acme.stratoware.io",
        "https://stratoware.io",
        "https://mcp.stratoware.io",
        "https://acme.stratoware.io.evil.test",
        "https://acme.stratoware.io:443",
        "https://x@acme.stratoware.io",
        "https://acme.stratoware.io/path",
        "https://acme.stratoware.io?token=secret",
        "https://acme.stratoware.io/#secret",
        "https://127.0.0.1",
        "https://acme.stratoware.io\n",
    ],
)
def test_only_tenant_origins_are_accepted(url):
    with pytest.raises(workspace.SetupError):
        workspace.workspace_origin(url)


def test_staging_and_trailing_slash():
    origin = workspace.workspace_origin("https://acme.staging.stratoware.io/")
    assert origin == "https://acme.staging.stratoware.io"
    assert workspace.server_name(origin) == "strato-acme-staging"


@pytest.mark.parametrize("port", ["", ":443", ":13100", ":65535"])
def test_local_workspace_requires_opt_in_and_preserves_stack_port(port):
    url = f"https://demo.stratoware.localhost{port}"
    with pytest.raises(workspace.SetupError):
        workspace.workspace_origin(url)
    origin = workspace.workspace_origin(url + "/", allow_local=True)
    assert origin == (url.removesuffix(":443") if port == ":443" else url)
    assert workspace.server_name(origin) == f"strato-demo-local-{port[1:] or '443'}"


@pytest.mark.parametrize(
    "url",
    [
        "http://demo.stratoware.localhost:13100",
        "https://demo.stratoware.localhost:0",
        "https://demo.stratoware.localhost:65536",
        "https://demo.stratoware.localhost:013100",
        "https://demo.stratoware.localhost:",
        "https://demo.stratoware.localhost:abc",
        "https://demo.stratoware.localhost.evil.test:13100",
        "https://mcp.stratoware.localhost:13100",
        "https://user@demo.stratoware.localhost:13100",
        "https://demo.stratoware.localhost:13100/path",
        "https://demo.stratoware.localhost:13100?token=secret",
        "https://demo.stratoware.localhost:13100\n",
        "https://127.0.0.1:13100",
        "https://localhost:13100",
        "https://[broken",
        "https://acme.stratoware.io:13100",
    ],
)
def test_local_opt_in_does_not_allow_other_origins(url):
    with pytest.raises(workspace.SetupError):
        workspace.workspace_origin(url, allow_local=True)


def test_local_stacks_do_not_overwrite_each_other_or_hosted_connections():
    text = ""
    names = []
    for origin in [
        ORIGIN,
        "https://acme.stratoware.localhost:13100",
        "https://acme.stratoware.localhost:13200",
    ]:
        text, name = configuration.prepare_config(text, origin)
        names.append(name)
    assert len(set(names)) == 3
    assert set(tomlkit.parse(text)["mcp_servers"]) == set(names)


def test_migration_preserves_other_settings_comments_and_policy():
    original = """# my settings
model = "example"
[mcp_servers.strato]
url = "https://acme.stratoware.io/api/mcp"
bearer_token_env_var = "OLD_TOKEN"
default_tools_approval_mode = "prompt"
enabled_tools = ["products_list_v1"]
http_headers = { Authorization = "old-secret", "X-Custom" = "retain" }
[mcp_servers.other]
url = "https://other.example/mcp"
"""
    updated, name = configuration.prepare_config(original, ORIGIN)
    data = tomlkit.parse(updated)
    assert name == "strato"
    assert updated.startswith("# my settings")
    assert "old-secret" not in updated and "OLD_TOKEN" not in updated
    assert data["model"] == "example"
    assert data["mcp_servers"]["other"]["url"] == "https://other.example/mcp"
    assert data["mcp_servers"][name]["http_headers"] == {"X-Custom": "retain"}
    assert data["mcp_servers"][name]["default_tools_approval_mode"] == "prompt"
    assert data["mcp_servers"][name]["enabled_tools"] == ["products_list_v1"]
    assert configuration.prepare_config(updated, ORIGIN)[0] == updated


def test_distinct_tenants_and_new_write_approval():
    text, name = configuration.prepare_config("", ORIGIN)
    text, other = configuration.prepare_config(text, "https://other.stratoware.io")
    servers = tomlkit.parse(text)["mcp_servers"]
    assert set(servers) == {name, other}
    assert servers[name]["default_tools_approval_mode"] == "writes"


@pytest.mark.parametrize(
    "original",
    [
        '[mcp_servers.strato-acme]\nurl="https://different.example/mcp"',
        '[mcp_servers.a]\nurl="https://acme.stratoware.io/api/mcp"\n[mcp_servers.b]\nurl="https://acme.stratoware.io/api/mcp"',
        'mcp_oauth_credentials_store="file"',
        "invalid [ toml",
    ],
)
def test_conflicting_configuration_is_not_replaced(original):
    with pytest.raises(workspace.SetupError):
        configuration.prepare_config(original, ORIGIN)


class TestNativeOAuth:
    @pytest.fixture
    def login(self, monkeypatch):
        run = Mock(return_value=SimpleNamespace(returncode=0))
        monkeypatch.setattr(configuration.subprocess, "run", run)
        monkeypatch.setattr(configuration, "remove_legacy_credential", Mock())
        return run

    def test_native_login_preserves_settings_and_never_handles_tokens(
        self, tmp_path, login
    ):
        original = b'model = "mine"\n'
        config = tmp_path / "config.toml"
        config.write_bytes(original)
        name = configuration.save_connection(tmp_path, ORIGIN, "/bin/codex")
        assert name == "strato-acme"
        login.assert_called_once_with(
            ["/bin/codex", "mcp", "login", name],
            capture_output=True,
            timeout=660,
            check=False,
        )
        data = tomlkit.parse(config.read_text())
        assert data["mcp_oauth_credentials_store"] == "keyring"
        assert data["mcp_servers"][name]["oauth"]["client_id"] == "strato-codex-prod"
        assert (
            data["mcp_servers"][name]["oauth"]["callback_url"]
            == "http://127.0.0.1/callback"
        )
        assert "http_headers_helper" not in data["mcp_servers"][name]
        assert (tmp_path / "config.toml.strato-backup").read_bytes() == original
        assert config.stat().st_mode & 0o777 == 0o600
        assert not (tmp_path / ".strato-setup.lock").exists()
        assert not (tmp_path / "strato-setup").exists()

    def test_failed_login_restores_settings_without_printing_output(
        self, tmp_path, login
    ):
        original = b'model = "mine"\n'
        config = tmp_path / "config.toml"
        config.write_bytes(original)
        login.return_value = SimpleNamespace(
            returncode=1, stdout=b"private", stderr=b"private"
        )
        with pytest.raises(workspace.SetupError) as error:
            configuration.save_connection(tmp_path, ORIGIN, "/bin/codex")
        assert "private" not in str(error.value)
        assert config.read_bytes() == original

    def test_concurrent_setup_does_not_start_login(self, tmp_path, login):
        with configuration.config_lock(tmp_path), pytest.raises(workspace.SetupError):
            configuration.save_connection(tmp_path, ORIGIN, "/bin/codex")
        login.assert_not_called()


def test_plaintext_or_unknown_keyring_is_rejected(monkeypatch):
    monkeypatch.setattr(credentials.keyring, "get_keyring", lambda: Mock())
    with pytest.raises(workspace.SetupError, match="OS credential store"):
        credentials.credential_store()


def test_existing_marketplace_is_reused(monkeypatch):
    commands = []

    def run(args, **kwargs):
        commands.append(args)
        return SimpleNamespace(
            stdout=json.dumps(
                {
                    "marketplaces": [
                        {
                            "name": "strato",
                            "marketplaceSource": {
                                "sourceType": "git",
                                "source": "https://github.com/stratoware/strato-agent-plugins.git",
                            },
                        }
                    ]
                }
            )
        )

    monkeypatch.setattr(configuration.subprocess, "run", run)
    configuration.install_plugin("codex")
    assert commands == [
        ["codex", "plugin", "marketplace", "list", "--json"],
        ["codex", "plugin", "add", "strato@strato"],
    ]


def test_foreign_marketplace_is_never_installed(monkeypatch):
    run = Mock(
        return_value=SimpleNamespace(
            stdout=json.dumps(
                {
                    "marketplaces": [
                        {
                            "name": "strato",
                            "marketplaceSource": {
                                "sourceType": "local",
                                "source": "/untrusted",
                            },
                        }
                    ]
                }
            )
        )
    )
    monkeypatch.setattr(configuration.subprocess, "run", run)
    with pytest.raises(workspace.SetupError, match="different marketplace"):
        configuration.install_plugin("codex")
    assert run.call_count == 1


@pytest.mark.parametrize("origin", [ORIGIN, "https://demo.stratoware.localhost:13100"])
def test_current_codex_accepts_generated_config(tmp_path, origin):
    if not configuration.shutil.which("codex"):
        pytest.skip("Codex is not installed")
    text, name = configuration.prepare_config("", origin)
    (tmp_path / "config.toml").write_text(text)
    result = configuration.subprocess.run(
        ["codex", "mcp", "get", name, "--json"],
        env={**os.environ, "CODEX_HOME": str(tmp_path)},
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout)["transport"]["url"] == origin + "/api/mcp"
    assert json.loads(result.stdout)["transport"]["http_headers_helper"] is None
