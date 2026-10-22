"""
Module de chiffrement utilisant Fernet (cryptography).

Ce module fournit les fonctionnalités de chiffrement/déchiffrement pour sécuriser
toutes les données sensibles de l'application.
"""

import getpass
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Gestionnaire de chiffrement utilisant Fernet.

    Génère des clés aléatoires et fournit des méthodes
    pour chiffrer/déchiffrer des données de manière sécurisée.
    """

    def __init__(self, user_identifier: Optional[str] = None) -> None:
        """
        Initialise le gestionnaire de chiffrement.

        Args:
            user_identifier: Conservé pour compatibilité; n'est pas utilisé pour dériver la clé.
        """
        self.user_identifier = user_identifier or getpass.getuser()
        self._fernet: Optional[Fernet] = None
        self._key: Optional[bytes] = None

    def generate_key(self) -> bytes:
        """
        Génère une clé aléatoire pour Fernet.

        Returns:
            Clé Fernet encodée en base64
        """
        self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)

        logger.debug("Clé de chiffrement générée avec succès")
        return self._key

    def set_key(self, key: bytes) -> None:
        """
        Définit une clé de chiffrement existante.

        Args:
            key: Clé Fernet encodée en base64

        Raises:
            ValueError: Si la clé est invalide
        """
        try:
            self._key = key
            self._fernet = Fernet(key)
            logger.debug("Clé de chiffrement définie avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la définition de la clé: {e}")
            raise ValueError("Clé de chiffrement invalide") from e

    def encrypt(self, data: str) -> bytes:
        """
        Chiffre une chaîne de caractères.

        Args:
            data: Données à chiffrer

        Returns:
            Données chiffrées

        Raises:
            RuntimeError: Si aucune clé n'est définie
        """
        if self._fernet is None:
            raise RuntimeError("Aucune clé de chiffrement définie. Appelez generate_key() ou set_key().")

        try:
            encrypted = self._fernet.encrypt(data.encode('utf-8'))
            logger.debug("Données chiffrées avec succès")
            return encrypted
        except Exception as e:
            logger.error(f"Erreur de chiffrement: {e}")
            raise

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Déchiffre des données.

        Args:
            encrypted_data: Données chiffrées

        Returns:
            Données déchiffrées en chaîne de caractères

        Raises:
            RuntimeError: Si aucune clé n'est définie
            InvalidToken: Si le déchiffrement échoue
        """
        if self._fernet is None:
            raise RuntimeError("Aucune clé de chiffrement définie. Appelez generate_key() ou set_key().")

        try:
            decrypted = self._fernet.decrypt(encrypted_data)
            logger.debug("Données déchiffrées avec succès")
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Échec du déchiffrement: token invalide")
            raise
        except Exception as e:
            logger.error(f"Erreur de déchiffrement: {e}")
            raise

    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Chiffre un fichier.

        Args:
            input_path: Chemin du fichier source
            output_path: Chemin du fichier chiffré

        Raises:
            RuntimeError: Si aucune clé n'est définie
            FileNotFoundError: Si le fichier source n'existe pas
        """
        if self._fernet is None:
            raise RuntimeError("Aucune clé de chiffrement définie.")

        try:
            with open(input_path, 'rb') as f:
                data = f.read()

            encrypted = self._fernet.encrypt(data)

            with open(output_path, 'wb') as f:
                f.write(encrypted)

            logger.info(f"Fichier chiffré: {input_path} -> {output_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chiffrement du fichier: {e}")
            raise

    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Déchiffre un fichier.

        Args:
            input_path: Chemin du fichier chiffré
            output_path: Chemin du fichier déchiffré

        Raises:
            RuntimeError: Si aucune clé n'est définie
            FileNotFoundError: Si le fichier source n'existe pas
            InvalidToken: Si le déchiffrement échoue
        """
        if self._fernet is None:
            raise RuntimeError("Aucune clé de chiffrement définie.")

        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted = self._fernet.decrypt(encrypted_data)

            with open(output_path, 'wb') as f:
                f.write(decrypted)

            logger.info(f"Fichier déchiffré: {input_path} -> {output_path}")
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement du fichier: {e}")
            raise

# Instance globale pour faciliter l'utilisation
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """
    Récupère l'instance globale du gestionnaire de chiffrement.

    Returns:
        Instance du gestionnaire de chiffrement
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
        _encryption_manager.generate_key()
    return _encryption_manager


def init_encryption(user_identifier: Optional[str] = None) -> EncryptionManager:
    """
    Initialise le gestionnaire de chiffrement global.

    Args:
        user_identifier: Identifiant utilisateur optionnel

    Returns:
        Instance du gestionnaire de chiffrement
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager(user_identifier)
        _encryption_manager.generate_key()
    return _encryption_manager
