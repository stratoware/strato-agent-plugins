from __future__ import annotations

import secrets

import keyring
from workspace import SetupError

SERVICE = "io.stratoware.codex"
SECURE_BACKENDS = {
    "keyring.backends.macOS.Keyring",
    "keyring.backends.Windows.WinVaultKeyring",
    "keyring.backends.SecretService.Keyring",
}


def credential_store():
    backend = keyring.get_keyring()
    name = f"{type(backend).__module__}.{type(backend).__name__}"
    if name not in SECURE_BACKENDS:
        raise SetupError(
            "An OS credential store is required: macOS Keychain, Windows Credential Manager, or Linux Secret Service."
        )
    return backend


def check_credential_store() -> None:
    backend = credential_store()
    name = "setup-probe-" + secrets.token_hex(16)
    try:
        backend.set_password(SERVICE, name, name)
        if backend.get_password(SERVICE, name) != name:
            raise SetupError(
                "The OS credential store could not verify secure storage. Unlock it and retry."
            )
    except Exception:
        raise SetupError(
            "The OS credential store is unavailable or locked. Unlock it and retry; no plaintext fallback is used."
        ) from None
    finally:
        try:
            backend.delete_password(SERVICE, name)
        except keyring.errors.PasswordDeleteError:
            pass


def remove_legacy_credential(origin: str) -> None:
    try:
        credential_store().delete_password(SERVICE, origin)
    except keyring.errors.PasswordDeleteError:
        pass
