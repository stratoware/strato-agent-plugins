from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

import tomlkit
from credentials import SERVICE, credential_store
from workspace import SetupError, is_local_workspace, server_name


def helper_command(uv: str, script: Path, origin: str) -> str:
    args = [
        uv,
        "run",
        "--quiet",
        "--locked",
        "--script",
        str(script),
        "headers",
        "--workspace-url",
        origin,
    ]
    if is_local_workspace(origin):
        args.append("--allow-local")
    return shlex.join(args)


def prepare_config(text: str, origin: str, command: str) -> tuple[str, str]:
    try:
        document = tomlkit.parse(text)
        servers = document.setdefault("mcp_servers", tomlkit.table())
        matching = [
            name
            for name, value in servers.items()
            if value.get("url", "").rstrip("/") == origin + "/api/mcp"
        ]
        if len(matching) > 1:
            raise SetupError(
                "Multiple MCP entries already use this workspace. Remove the duplicate in Codex Settings first."
            )
        name = matching[0] if matching else server_name(origin)
        if not matching and name in servers:
            raise SetupError(
                f"The MCP entry {name} points elsewhere. Rename it in Codex Settings first."
            )
        server = servers.setdefault(name, tomlkit.table())
        if "command" in server or "oauth" in server:
            raise SetupError(
                "This workspace has a different connection method. Remove that entry in Codex Settings before guided setup."
            )
        server["url"] = origin + "/api/mcp"
        server["http_headers_helper"] = command
        server["enabled"] = True
        server.setdefault("default_tools_approval_mode", "writes")
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


def save_connection(
    home: Path,
    origin: str,
    token: str,
    uv: str,
    confirm: Callable[[], None] | None = None,
) -> str:
    store = credential_store()
    with config_lock(home):
        config = home / "config.toml"
        if config.is_symlink():
            raise SetupError(
                "Codex config.toml is a symbolic link. Configure this managed installation manually."
            )
        previous = config.read_bytes() if config.exists() else b""
        destination = home / "strato-setup"
        if destination.is_symlink():
            raise SetupError(
                "The Strato helper directory is a symbolic link. Remove that link before setup."
            )
        command = helper_command(uv, destination / "setup_codex.py", origin)
        updated, name = prepare_config(previous.decode(), origin, command)
        destination.mkdir(mode=0o700, exist_ok=True)
        source = Path(__file__).parent
        for item in source.iterdir():
            if item.suffix in {".py", ".html", ".lock"}:
                target = destination / item.name
                if item.resolve() != target.resolve():
                    atomic_write(target, item.read_bytes())
        old_token = store.get_password(SERVICE, origin)
        store.set_password(SERVICE, origin, token)
        try:
            if (config.read_bytes() if config.exists() else b"") != previous:
                raise SetupError("Codex settings changed during setup. Try again.")
            if previous and not (home / "config.toml.strato-backup").exists():
                atomic_write(home / "config.toml.strato-backup", previous)
            atomic_write(config, updated.encode())
            if confirm is not None:
                confirm()
        except BaseException:
            if config.exists() and config.read_bytes() == updated.encode():
                if previous:
                    atomic_write(config, previous)
                else:
                    config.unlink()
            if old_token is None:
                store.delete_password(SERVICE, origin)
            else:
                store.set_password(SERVICE, origin, old_token)
            raise
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
        raise SetupError(
            "Guided setup currently supports macOS and Linux. Use the manual connection guide on Windows."
        )
    codex, uv = shutil.which("codex"), shutil.which("uv")
    if not codex or not uv:
        raise SetupError(
            "Codex and uv must be available. Ask the setup chat to locate them or help install the missing prerequisite."
        )
    try:
        result = subprocess.run(
            [
                codex,
                "-c",
                'mcp_servers.strato_setup_probe.url="https://example.invalid/mcp"',
                "-c",
                'mcp_servers.strato_setup_probe.http_headers_helper="strato-setup-probe"',
                "mcp",
                "get",
                "strato_setup_probe",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        if not json.loads(result.stdout)["transport"].get("http_headers_helper"):
            raise ValueError()
    except (subprocess.SubprocessError, OSError, ValueError, KeyError):
        raise SetupError(
            "This Codex version does not support credential helpers. Update Codex before guided setup."
        ) from None
    return codex, uv
