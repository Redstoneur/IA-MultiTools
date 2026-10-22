"""Tests pour la gestion du mot de passe d'application."""

from src.ia_multitools.core import authentication as auth_module


class FakeKeyring:
    """Double de test minimal pour le trousseau."""

    def __init__(self) -> None:
        self._store = {}

    def is_available(self) -> bool:
        return True

    def set_password(self, username: str, password: str) -> bool:
        self._store[username] = password
        return True

    def get_password(self, username: str):
        return self._store.get(username)

    def delete_password(self, username: str) -> bool:
        return self._store.pop(username, None) is not None


def test_password_lifecycle(monkeypatch):
    """Définit, vérifie et supprime un mot de passe."""
    fake_keyring = FakeKeyring()
    monkeypatch.setitem(
        auth_module.AuthenticationManager.__init__.__globals__,
        "get_keyring_manager",
        lambda: fake_keyring,
    )

    manager = auth_module.AuthenticationManager(lock_enabled=True, auto_lock_minutes=0)

    assert manager.has_password() is False
    assert manager.set_password("secret123") is True
    assert manager.has_password() is True
    assert manager.verify_password("secret123") is True
    assert manager.verify_password("bad-password") is False
    assert manager.remove_password() is True
    assert manager.has_password() is False


