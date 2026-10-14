from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

import tomlkit
from credentials import remove_legacy_credential
from workspace import SetupError, is_local_workspace, server_name


def native_client_id(origin: str) -> str:
    environment = (
        "local"
        if is_local_workspace(origin)
        else "staging"
        if urlsplit(origin).hostname.endswith(".staging.stratoware.io")
        else "prod"
    )
    return f"strato-codex-{environment}"


def prepare_config(text: str, origin: str) -> tuple[str, str]:
    try:
        document = tomlkit.parse(text)
        if document.get("mcp_oauth_credentials_store") == "file":
            raise SetupError(
                "Codex is configured to store OAuth credentials in a file. Select OS credential storage before connecting Strato."
            )
        servers = document.setdefault("mcp_servers", tomlkit.table())
        matching = [
            name
            for name, value in servers.items()
            if value.get("url", "").rstrip("/") == origin + "/api/mcp"
        ]
        if len(matching) > 1:
            raise SetupError(
                "Multiple MCP entries use this workspace. Resolve the duplicate in Codex Settings first."
            )
        name = matching[0] if matching else server_name(origin)
        if not matching and name in servers:
            raise SetupError(
                f"The MCP entry {name} points elsewhere. Rename it in Codex Settings first."
            )
        server = servers.setdefault(name, tomlkit.table())
        if "command" in server:
            raise SetupError(
                "This workspace uses a different transport. Remove that entry in Codex Settings before setup."
            )
        helper = server.get("http_headers_helper", "")
        if helper and not (
            "setup_codex.py" in helper and "headers" in helper and origin in helper
        ):
            raise SetupError(
                "This workspace uses a custom credential helper. Remove it in Codex Settings before setup."
            )
        document["mcp_oauth_credentials_store"] = "keyring"
        server.update(
            url=origin + "/api/mcp", oauth_resource=origin + "/api/mcp", enabled=True
        )
        server["oauth"] = {
            "client_id": native_client_id(origin),
            "callback_url": "http://127.0.0.1/callback",
        }
        server["scopes"] = ["dhf:records:read", "dhf:development:write"]
        server.setdefault("default_tools_approval_mode", "writes")
        server.pop("http_headers_helper", None)
        server.pop("bearer_token_env_var", None)
        for field in ("http_headers", "env_http_headers"):
            for header in list(server.get(field, {})):
                if header.lower() == "authorization":
                    del server[field][header]
        return tomlkit.dumps(document), name
    except SetupError:
        raise
    except (ValueError, TypeError, AttributeError):
        raise SetupError(
            "Codex configuration could not be read. Fix its syntax before running setup."
        ) from None


@contextmanager
def config_lock(home: Path):
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = home / ".strato-setup.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SetupError(
            "Another Strato setup is running. Close it before trying again."
        ) from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def atomic_write(path: Path, content: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".strato-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_connection(home: Path, origin: str, codex: str) -> str:
    with config_lock(home):
        config = home / "config.toml"
        if config.is_symlink():
            raise SetupError(
                "Codex config.toml is managed through a symbolic link. Contact your administrator before setup."
            )
        previous = config.read_bytes() if config.exists() else b""
        updated, name = prepare_config(previous.decode(), origin)
        if previous and not (home / "config.toml.strato-backup").exists():
            atomic_write(home / "config.toml.strato-backup", previous)
        atomic_write(config, updated.encode())
        try:
            result = subprocess.run(
                [codex, "mcp", "login", name],
                capture_output=True,
                timeout=660,
                check=False,
            )
            if result.returncode:
                raise SetupError(
                    "Authorization did not complete. Sign in and approve access in the browser, then try setup again. If consent succeeded, you can disconnect the unused authorization in Strato."
                )
        except BaseException:
            if config.exists() and config.read_bytes() == updated.encode():
                if previous:
                    atomic_write(config, previous)
                else:
                    config.unlink()
            raise
        remove_legacy_credential(origin)
        return name


def install_plugin(codex: str) -> None:
    def run(*args: str) -> str:
        try:
            return subprocess.run(
                [codex, "plugin", *args],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            ).stdout
        except (subprocess.SubprocessError, OSError):
            raise SetupError(
                "Codex could not install the Strato plugin. Check GitHub access, plugin policy, and your Codex version."
            ) from None

    try:
        marketplaces = json.loads(run("marketplace", "list", "--json"))["marketplaces"]
        existing = next(
            (item for item in marketplaces if item["name"] == "strato"), None
        )
        if existing:
            source = existing.get("marketplaceSource", {})
            if (
                source.get("sourceType") != "git"
                or source.get("source", "").removesuffix(".git")
                != "https://github.com/stratoware/strato-agent-plugins"
            ):
                raise SetupError(
                    "A different marketplace named strato is already configured. Resolve it in Codex before continuing."
                )
        else:
            run(
                "marketplace",
                "add",
                "stratoware/strato-agent-plugins",
                "--ref",
                "stable",
            )
    except SetupError:
        raise
    except (ValueError, KeyError, TypeError):
        raise SetupError(
            "Could not inspect Codex plugin sources. Update Codex before running guided setup."
        ) from None
    run("add", "strato@strato")


def executables() -> tuple[str, str]:
    if os.name == "nt":
        raise SetupError("Guided setup currently supports macOS and Linux.")
    codex, uv = shutil.which("codex"), shutil.which("uv")
    if not codex or not uv:
        raise SetupError(
            "Codex and uv must be available. Ask the setup chat to locate or install them."
        )
    try:
        result = subprocess.run(
            [codex, "--version"], check=True, capture_output=True, text=True, timeout=20
        )
        version = re.search(r"codex-cli (\d+)\.(\d+)\.(\d+)", result.stdout)
        if version is None or tuple(map(int, version.groups())) < (0, 160, 0):
            raise ValueError()
    except (subprocess.SubprocessError, OSError, ValueError):
        raise SetupError(
            "Update Codex to version 0.160.0 or later before connecting Strato."
        ) from None
    return codex, uv
