"""
Gestionnaire de stockage sécurisé.

Ce module fournit un stockage sécurisé pour les données sensibles en combinant
le chiffrement Fernet et le trousseau système.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

from cryptography.fernet import Fernet
from .encryption import EncryptionManager, get_encryption_manager
from .keyring_manager import KeyringManager, get_keyring_manager

logger = logging.getLogger(__name__)


class SecureStorage:
    """
    Gestionnaire de stockage sécurisé pour les données sensibles.

    Utilise Fernet pour les fichiers et conserve la clé de chiffrement dans le
    trousseau système.
    """

    def __init__(
        self,
        storage_dir: Path,
        encryption_manager: Optional[EncryptionManager] = None,
        keyring_manager: Optional[KeyringManager] = None,
        use_keyring: bool = True
    ) -> None:
        """
        Initialise le gestionnaire de stockage sécurisé.

        Args:
            storage_dir: Répertoire de stockage
            encryption_manager: Gestionnaire de chiffrement (optionnel)
            keyring_manager: Gestionnaire de trousseau (optionnel)
            use_keyring: Exiger le trousseau système pour protéger la clé de chiffrement
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.encryption_manager = encryption_manager or get_encryption_manager()
        self.keyring_manager = keyring_manager or get_keyring_manager()
        self.use_keyring = use_keyring and self.keyring_manager.is_available()

        if use_keyring and not self.use_keyring:
            raise RuntimeError(
                "Un trousseau système fonctionnel est requis pour chiffrer les données persistées."
            )

        if self.use_keyring:
            encoded_key = self.keyring_manager.get_encryption_key()
            if encoded_key is None:
                if any(self.storage_dir.glob("*.enc")):
                    raise RuntimeError(
                        "La clé de chiffrement est absente alors que des données chiffrées existent."
                    )
                key = Fernet.generate_key()
                if not self.keyring_manager.set_encryption_key(key.decode("ascii")):
                    raise RuntimeError(
                        "Impossible d'enregistrer la clé de chiffrement dans le trousseau système."
                    )
            else:
                key = encoded_key.encode("ascii")
            self.encryption_manager.set_key(key)
        else:
            self.encryption_manager.generate_key()

        logger.info(f"Stockage sécurisé initialisé: {self.storage_dir}")
        logger.debug(f"Utilisation du trousseau système: {self.use_keyring}")

    def _get_file_path(self, filename: str) -> Path:
        """
        Construit le chemin complet d'un fichier.

        Args:
            filename: Nom du fichier

        Returns:
            Chemin complet
        """
        return self.storage_dir / filename

    def save_encrypted(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        Sauvegarde des données chiffrées dans un fichier.

        Args:
            filename: Nom du fichier (sera suffixé par .enc)
            data: Données à sauvegarder (dictionnaire)

        Returns:
            True si la sauvegarde a réussi
        """
        try:
            if self.use_keyring:
                encoded_key = self.keyring_manager.get_encryption_key()
                if encoded_key is None:
                    logger.error("Clé de chiffrement absente du trousseau système")
                    return False
                self.encryption_manager.set_key(encoded_key.encode("ascii"))

            # Sérialiser en JSON
            json_data = json.dumps(data, indent=2, ensure_ascii=False)

            # Chiffrer
            encrypted_data = self.encryption_manager.encrypt(json_data)

            # Écrire dans le fichier
            file_path = self._get_file_path(f"{filename}.enc")
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)

            logger.info(f"Données sauvegardées et chiffrées: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde chiffrée: {e}")
            return False

    def load_encrypted(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Charge des données chiffrées depuis un fichier.

        Args:
            filename: Nom du fichier (sans extension .enc)

        Returns:
            Données déchiffrées (dictionnaire) ou None en cas d'erreur
        """
        file_path = self._get_file_path(f"{filename}.enc")

        if not file_path.exists():
            logger.warning(f"Fichier non trouvé: {file_path}")
            return None

        try:
            # Lire le fichier chiffré
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            # Déchiffrer
            json_data = self.encryption_manager.decrypt(encrypted_data)

            # Désérialiser
            data = json.loads(json_data)

            logger.debug(f"Données chargées et déchiffrées: {file_path}")
            return data

        except Exception as e:
            logger.error(f"Erreur lors du chargement chiffré: {e}")
            return None

    def delete_encrypted(self, filename: str) -> bool:
        """
        Supprime un fichier chiffré.

        Args:
            filename: Nom du fichier (sans extension .enc)

        Returns:
            True si la suppression a réussi
        """
        file_path = self._get_file_path(f"{filename}.enc")

        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Fichier supprimé: {file_path}")
                return True
            else:
                logger.warning(f"Fichier non trouvé: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False

    def file_exists(self, filename: str) -> bool:
        """
        Vérifie si un fichier chiffré existe.

        Args:
            filename: Nom du fichier (sans extension .enc)

        Returns:
            True si le fichier existe
        """
        file_path = self._get_file_path(f"{filename}.enc")
        return file_path.exists()

    def list_files(self) -> list[str]:
        """
        Liste tous les fichiers chiffrés.

        Returns:
            Liste des noms de fichiers (sans extension .enc)
        """
        try:
            files = [f.stem for f in self.storage_dir.glob("*.enc")]
            logger.debug(f"Fichiers chiffrés trouvés: {files}")
            return files
        except Exception as e:
            logger.error(f"Erreur lors du listage des fichiers: {e}")
            return []

    def clear_all(self) -> bool:
        """
        Supprime tous les fichiers chiffrés.

        Returns:
            True si la suppression a réussi
        """
        try:
            for file_path in self.storage_dir.glob("*.enc"):
                file_path.unlink()
            logger.warning("Tous les fichiers chiffrés ont été supprimés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de tous les fichiers: {e}")
            return False

    def backup_to_keyring(self, key_name: str, data: str) -> bool:
        """
        Sauvegarde une donnée dans le trousseau système.

        Args:
            key_name: Nom de la clé
            data: Donnée à sauvegarder

        Returns:
            True si la sauvegarde a réussi
        """
        if not self.use_keyring:
            logger.warning("Trousseau système non disponible ou désactivé")
            return False

        return self.keyring_manager.set_password(key_name, data)

    def restore_from_keyring(self, key_name: str) -> Optional[str]:
        """
        Restaure une donnée depuis le trousseau système.

        Args:
            key_name: Nom de la clé

        Returns:
            Donnée restaurée ou None
        """
        if not self.use_keyring:
            logger.warning("Trousseau système non disponible ou désactivé")
            return None

        return self.keyring_manager.get_password(key_name)


# Instance globale
_secure_storage: Optional[SecureStorage] = None


def get_secure_storage(storage_dir: Optional[Path] = None) -> SecureStorage:
    """
    Récupère l'instance globale du stockage sécurisé.

    Args:
        storage_dir: Répertoire de stockage (optionnel, utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du stockage sécurisé
    """
    global _secure_storage
    if _secure_storage is None:
        if storage_dir is None:
            raise ValueError("Le répertoire de stockage doit être fourni lors de l'initialisation")
        _secure_storage = SecureStorage(storage_dir)
    return _secure_storage


def init_secure_storage(
    storage_dir: Path,
    use_keyring: bool = True
) -> SecureStorage:
    """
    Initialise le stockage sécurisé global.

    Args:
        storage_dir: Répertoire de stockage
        use_keyring: Utiliser le trousseau système

    Returns:
        Instance du stockage sécurisé
    """
    global _secure_storage
    _secure_storage = SecureStorage(storage_dir, use_keyring=use_keyring)
    return _secure_storage
