"""
Tests pour le module d'encryption.
"""

import pytest
from src.ia_multitools.core.encryption import EncryptionManager


def test_encryption_manager_initialization():
    """Test de l'initialisation du gestionnaire de chiffrement."""
    manager = EncryptionManager()
    assert manager is not None
    assert manager.user_identifier is not None


def test_key_generation():
    """Test de la génération de clé."""
    manager = EncryptionManager()
    key = manager.generate_key()
    assert key is not None
    assert len(key) > 0


def test_encrypt_decrypt():
    """Test de chiffrement et déchiffrement."""
    manager = EncryptionManager()
    manager.generate_key()

    original_text = "Ceci est un test de chiffrement"

    # Chiffrer
    encrypted = manager.encrypt(original_text)
    assert encrypted is not None
    assert encrypted != original_text.encode()

    # Déchiffrer
    decrypted = manager.decrypt(encrypted)
    assert decrypted == original_text


def test_encrypt_special_characters():
    """Test de chiffrement avec caractères spéciaux."""
    manager = EncryptionManager()
    manager.generate_key()

    original_text = "Texte avec accents: éèêàù çñ 🔐"
    encrypted = manager.encrypt(original_text)
    decrypted = manager.decrypt(encrypted)

    assert decrypted == original_text


def test_invalid_decryption():
    """Test de déchiffrement avec une mauvaise clé."""
    manager1 = EncryptionManager(user_identifier="user1")
    manager1.generate_key()

    manager2 = EncryptionManager(user_identifier="user2")
    manager2.generate_key()

    original_text = "Secret message"
    encrypted = manager1.encrypt(original_text)

    # Tenter de déchiffrer avec une autre clé
    with pytest.raises(Exception):
        manager2.decrypt(encrypted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

