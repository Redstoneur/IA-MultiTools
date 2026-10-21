"""
Module de chiffrement utilisant Fernet (cryptography).

Ce module fournit les fonctionnalités de chiffrement/déchiffrement pour sécuriser
toutes les données sensibles de l'application.
"""

import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Gestionnaire de chiffrement utilisant Fernet.

    Génère des clés de chiffrement liées au compte utilisateur et fournit des méthodes
    pour chiffrer/déchiffrer des données de manière sécurisée.
    """

    def __init__(self, user_identifier: Optional[str] = None) -> None:
        """
        Initialise le gestionnaire de chiffrement.

        Args:
            user_identifier: Identifiant unique de l'utilisateur (utilisé pour dériver la clé).
                           Si None, utilise le nom d'utilisateur système.
        """
        self.user_identifier = user_identifier or self._get_system_user()
        self._fernet: Optional[Fernet] = None
        self._key: Optional[bytes] = None

    def _get_system_user(self) -> str:
        """
        Récupère l'identifiant de l'utilisateur système.

        Returns:
            Nom d'utilisateur système
        """
        import getpass
        return getpass.getuser()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Dérive une clé de chiffrement depuis un mot de passe.

        Args:
            password: Mot de passe source
            salt: Salt pour la dérivation

        Returns:
            Clé de chiffrement de 32 bytes
        """
        kdf = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,  # 100k iterations
            dklen=32
        )
        return base64.urlsafe_b64encode(kdf)

    def generate_key(self, salt: Optional[bytes] = None) -> bytes:
        """
        Génère une clé de chiffrement liée au compte utilisateur.

        Args:
            salt: Salt optionnel pour la dérivation. Si None, un salt par défaut est utilisé.

        Returns:
            Clé Fernet encodée en base64
        """
        if salt is None:
            # Salt par défaut basé sur l'identifiant utilisateur
            salt = hashlib.sha256(self.user_identifier.encode('utf-8')).digest()

        # Dériver une clé depuis l'identifiant utilisateur
        self._key = self._derive_key(self.user_identifier, salt)
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

    def rotate_key(self, old_key: bytes, new_password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Rotate les clés de chiffrement (ré-chiffrement avec une nouvelle clé).

        Args:
            old_key: Ancienne clé de chiffrement
            new_password: Nouveau mot de passe pour dériver la nouvelle clé
            salt: Salt optionnel pour la nouvelle clé

        Returns:
            Nouvelle clé de chiffrement
        """
        if salt is None:
            salt = os.urandom(32)

        new_key = self._derive_key(new_password, salt)
        logger.info("Rotation de clé effectuée avec succès")
        return new_key


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
    _encryption_manager = EncryptionManager(user_identifier)
    _encryption_manager.generate_key()
    return _encryption_manager

