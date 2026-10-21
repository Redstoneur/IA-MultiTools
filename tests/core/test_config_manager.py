"""
Tests pour le gestionnaire de configuration.
"""

import pytest
import tempfile
from pathlib import Path
from src.ia_multitools.core.config_manager import ConfigManager, AppConfig


def test_config_manager_initialization():
    """Test de l'initialisation du gestionnaire de configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(debug_mode=True)
        assert manager is not None
        assert manager.config is not None


def test_default_config():
    """Test de la configuration par défaut."""
    manager = ConfigManager(debug_mode=True)
    config = manager.get_config()

    assert config.ai.base_url == "http://127.0.0.1:1234/v1"
    assert config.ai.model == "meta-llama-3.1-8b-instruct"
    assert config.ai.temperature == 0.2
    assert config.security.encryption_enabled is True
    assert config.history.enabled is True


def test_config_save_load():
    """Test de sauvegarde et chargement de configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
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


def test_config_validation():
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

