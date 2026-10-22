"""
Gestionnaire du trousseau système (Keyring).

Ce module fournit une interface pour stocker et récupérer des secrets dans le trousseau
système de manière sécurisée (DPAPI sur Windows, Secret Service sur Linux).
"""

import logging
from typing import Optional
import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)


class KeyringManager:
    """
    Gestionnaire du trousseau système multi-plateforme.

    Utilise le module keyring pour accéder au trousseau système natif:
    - Windows: DPAPI / Credential Manager
    - Linux: Secret Service / GNOME Keyring / KWallet
    """

    SERVICE_NAME = "IA-MultiTools"

    def __init__(self) -> None:
        """Initialise le gestionnaire de trousseau."""
        self._available = self._check_availability()
        if self._available:
            logger.info(f"Trousseau système disponible: {keyring.get_keyring().__class__.__name__}")
        else:
            logger.warning("Aucun trousseau système fonctionnel n'est disponible")

    def _check_availability(self) -> bool:
        """
        Vérifie si un trousseau système est disponible.

        Returns:
            True si un trousseau est disponible et fonctionnel
        """
        try:
            current_keyring = keyring.get_keyring()
            return current_keyring.priority > 0
        except Exception as e:
            logger.warning(f"Impossible de vérifier le trousseau: {e}")
            return False

    def is_available(self) -> bool:
        """
        Vérifie si le trousseau système est disponible.

        Returns:
            True si disponible
        """
        return self._available

    def set_password(self, username: str, password: str) -> bool:
        """
        Stocke un mot de passe dans le trousseau système.

        Args:
            username: Nom d'utilisateur (clé)
            password: Mot de passe à stocker

        Returns:
            True si le stockage a réussi, False sinon
        """
        if not self._available:
            logger.warning("Trousseau système non disponible")
            return False

        try:
            keyring.set_password(self.SERVICE_NAME, username, password)
            logger.debug(f"Mot de passe stocké pour l'utilisateur: {username}")
            return True
        except KeyringError as e:
            logger.error("Erreur lors du stockage dans le trousseau: %s", type(e).__name__)
            return False
        except Exception as e:
            logger.error("Erreur inattendue lors du stockage dans le trousseau: %s", type(e).__name__)
            return False

    def get_password(self, username: str) -> Optional[str]:
        """
        Récupère un mot de passe depuis le trousseau système.

        Args:
            username: Nom d'utilisateur (clé)

        Returns:
            Mot de passe si trouvé, None sinon
        """
        if not self._available:
            logger.warning("Trousseau système non disponible")
            return None

        try:
            password = keyring.get_password(self.SERVICE_NAME, username)
            if password:
                logger.debug(f"Mot de passe récupéré pour l'utilisateur: {username}")
            else:
                logger.debug(f"Aucun mot de passe trouvé pour l'utilisateur: {username}")
            return password
        except KeyringError as e:
            logger.error("Erreur lors de la récupération depuis le trousseau: %s", type(e).__name__)
            raise RuntimeError("Impossible de lire le trousseau système") from e
        except Exception as e:
            logger.error("Erreur inattendue lors de la récupération depuis le trousseau: %s", type(e).__name__)
            raise RuntimeError("Impossible de lire le trousseau système") from e

    def delete_password(self, username: str) -> bool:
        """
        Supprime un mot de passe du trousseau système.

        Args:
            username: Nom d'utilisateur (clé)

        Returns:
            True si la suppression a réussi, False sinon
        """
        if not self._available:
            logger.warning("Trousseau système non disponible")
            return False

        try:
            keyring.delete_password(self.SERVICE_NAME, username)
            logger.info(f"Mot de passe supprimé pour l'utilisateur: {username}")
            return True
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"Aucun mot de passe à supprimer pour: {username}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du mot de passe: {e}")
            return False

    def set_api_key(self, api_key: str) -> bool:
        """
        Stocke la clé API dans le trousseau système.

        Args:
            api_key: Clé API OpenAI

        Returns:
            True si le stockage a réussi
        """
        return self.set_password("openai_api_key", api_key)

    def get_api_key(self) -> Optional[str]:
        """
        Récupère la clé API depuis le trousseau système.

        Returns:
            Clé API si trouvée, None sinon
        """
        return self.get_password("openai_api_key")

    def delete_api_key(self) -> bool:
        """
        Supprime la clé API du trousseau système.

        Returns:
            True si la suppression a réussi
        """
        return self.delete_password("openai_api_key")

    def set_encryption_key(self, encryption_key: str) -> bool:
        """
        Stocke la clé de chiffrement dans le trousseau système.

        Args:
            encryption_key: Clé de chiffrement (base64)

        Returns:
            True si le stockage a réussi
        """
        return self.set_password("encryption_key", encryption_key)

    def get_encryption_key(self) -> Optional[str]:
        """
        Récupère la clé de chiffrement depuis le trousseau système.

        Returns:
            Clé de chiffrement si trouvée, None sinon
        """
        return self.get_password("encryption_key")

    def delete_encryption_key(self) -> bool:
        """
        Supprime la clé de chiffrement du trousseau système.

        Returns:
            True si la suppression a réussi
        """
        return self.delete_password("encryption_key")


# Instance globale
_keyring_manager: Optional[KeyringManager] = None


def get_keyring_manager() -> KeyringManager:
    """
    Récupère l'instance globale du gestionnaire de trousseau.

    Returns:
        Instance du gestionnaire de trousseau
    """
    global _keyring_manager
    if _keyring_manager is None:
        _keyring_manager = KeyringManager()
    return _keyring_manager
