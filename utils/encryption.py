from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


# -----------------------------
# Key Generation
# -----------------------------
def generate_key() -> str:
    """Generate a new Fernet key."""
    return Fernet.generate_key().decode()


# -----------------------------
# Fernet Instance Loader
# -----------------------------
def get_fernet() -> Fernet:
    """
    Load Fernet instance from settings.
    Validates presence + key format.
    """
    key = getattr(settings, "FERNET_KEY", None)
    if not key:
        raise ValueError("FERNET_KEY is missing in Django settings.")

    if isinstance(key, str):
        key = key.encode()

    try:
        return Fernet(key)
    except Exception as exc:
        raise ValueError(f"Invalid CUSTOM_FERNET_KEY. Details: {exc}")


# Lazy-loaded global Fernet instance
try:
    fernet = get_fernet()
except Exception:
    # Allow script execution without Django settings
    fernet = None


# -----------------------------
# Encrypt / Decrypt wrappers
# -----------------------------
def encrypt_value(text: str | None) -> str | None:
    """
    Encrypt plain text.
    """
    if text is None:
        return None

    if fernet is None:
        raise RuntimeError("Cannot encrypt: Fernet key not loaded.")

    return fernet.encrypt(text.encode()).decode()


def decrypt_value(token: str | None) -> str | None:
    """
    Decrypt encrypted token.
    """
    if token is None:
        return None

    if fernet is None:
        raise RuntimeError("Cannot decrypt: Fernet key not loaded.")

    try:
        return fernet.decrypt(token.encode()).decode()

    except InvalidToken:
        raise ValueError("Decryption failed – invalid key or corrupted token.")


# -----------------------------
# CLI Mode: Generate a key
# -----------------------------
if __name__ == "__main__":
    print("\n🔐 Generated Fernet Key:\n")
    key = generate_key()
    print(key)
    print("\nAdd this to your .env file:")
    print(f'FERNET_KEY="{key}"')
    print()
