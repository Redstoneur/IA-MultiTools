"""
Tests pour le gestionnaire de configuration.
"""

import pytest
import pytest

from src.ia_multitools.core.config_manager import ConfigManager
from src.ia_multitools.core.secure_storage import SecureStorage


class FakeKeyring:
    """Trousseau en mémoire réservé aux tests."""

    def __init__(self):
        self.entries = {}

    def is_available(self):
        return True

    def get_encryption_key(self):
        return self.entries.get("encryption_key")

    def set_encryption_key(self, value):
        self.entries["encryption_key"] = value
        return True

    def get_api_key(self):
        return self.entries.get("openai_api_key")

    def set_api_key(self, value):
        self.entries["openai_api_key"] = value
        return True

    def delete_api_key(self):
        self.entries.pop("openai_api_key", None)
        return True


@pytest.fixture
def fake_keyring(tmp_path, monkeypatch):
    keyring = FakeKeyring()
    monkeypatch.setitem(
        ConfigManager.__init__.__globals__,
        "get_keyring_manager",
        lambda: keyring,
    )
    monkeypatch.setitem(
        SecureStorage.__init__.__globals__,
        "get_keyring_manager",
        lambda: keyring,
    )
    monkeypatch.setattr(ConfigManager, "_get_config_dir", lambda _self: tmp_path)
    return keyring


def test_config_manager_initialization(fake_keyring):
    """Test de l'initialisation du gestionnaire de configuration."""
    manager = ConfigManager(debug_mode=True)
    assert manager is not None
    assert manager.config is not None


def test_default_config(fake_keyring):
    """Test de la configuration par défaut."""
    manager = ConfigManager(debug_mode=True)
    config = manager.get_config()

    assert config.ai.base_url == "http://127.0.0.1:1234/v1"
    assert config.ai.model == "meta-llama-3.1-8b-instruct"
    assert config.ai.temperature == 0.2
    assert config.security.encryption_enabled is True
    assert config.history.enabled is True


def test_config_save_load(fake_keyring):
    """Test de sauvegarde et chargement de configuration."""
    manager = ConfigManager(debug_mode=True)

    # Modifier la configuration
    manager.update_ai_config(model="test-model", temperature=0.5)

    # Sauvegarder
    assert manager.save() is True

    # Créer un nouveau gestionnaire et charger
    manager2 = ConfigManager(debug_mode=True)
    manager2.load()

    config = manager2.get_config()
    assert config.ai.model == "test-model"
    assert config.ai.temperature == 0.5


def test_config_validation(fake_keyring):
    """Test de validation de configuration."""
    manager = ConfigManager(debug_mode=True)

    # Configuration valide
    valid, errors = manager.validate()
    assert valid is True
    assert len(errors) == 0

    # Configuration invalide
    manager.config.ai.temperature = 5.0  # Hors limites
    valid, errors = manager.validate()
    assert valid is False
    assert len(errors) > 0


def test_api_key_not_persisted_in_config_payload(fake_keyring):
    """La clé API ne doit jamais être écrite dans le payload de config."""
    manager = ConfigManager(debug_mode=True)
    manager.config.ai.api_key = "sk-secret"

    captured_data = {}

    def fake_save_encrypted(_filename, data):
        captured_data.update(data)
        return True

    setattr(manager.storage, "save_encrypted", fake_save_encrypted)

    assert manager.save() is True
    assert "api_key" not in captured_data["ai"]
    assert fake_keyring.entries["openai_api_key"] == "sk-secret"


def test_api_key_is_loaded_only_from_keyring(fake_keyring):
    manager = ConfigManager(debug_mode=True)
    manager.config.ai.api_key = "sk-test-secret"
    assert manager.save() is True

    reloaded_manager = ConfigManager(debug_mode=True)
    assert reloaded_manager.load() is True
    assert reloaded_manager.config.ai.api_key == "sk-test-secret"


def test_api_key_save_fails_if_keyring_becomes_unavailable(fake_keyring):
    manager = ConfigManager(debug_mode=True)
    manager.config.ai.api_key = "sk-test-secret"
    fake_keyring.is_available = lambda: False

    assert manager.save() is False
    assert not manager.storage.file_exists(manager.CONFIG_FILENAME)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
