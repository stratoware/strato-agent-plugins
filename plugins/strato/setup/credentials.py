from __future__ import annotations

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


def read_token(origin: str) -> str:
    token = credential_store().get_password(SERVICE, origin)
    if not token:
        raise SetupError(
            "No Strato token is saved. Run guided setup for this workspace again."
        )
    return token
