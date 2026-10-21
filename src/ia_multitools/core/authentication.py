"""
Module d'authentification et de verrouillage d'application.

Gère l'authentification système optionnelle et le verrouillage automatique.
"""

import logging
import time
from typing import Optional, Callable
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """
    Gestionnaire d'authentification et de verrouillage de l'application.

    Fournit des mécanismes de verrouillage optionnel et d'auto-verrouillage
    après une période d'inactivité.
    """

    def __init__(self, lock_enabled: bool = False, auto_lock_minutes: int = 0) -> None:
        """
        Initialise le gestionnaire d'authentification.

        Args:
            lock_enabled: Active le verrouillage de l'application
            auto_lock_minutes: Délai en minutes avant le verrouillage automatique (0 = désactivé)
        """
        self.lock_enabled = lock_enabled
        self.auto_lock_minutes = auto_lock_minutes
        self.is_locked = False
        self.last_activity = datetime.now()

        self._lock_callback: Optional[Callable[[], None]] = None
        self._auto_lock_thread: Optional[threading.Thread] = None
        self._stop_auto_lock = threading.Event()

        if self.auto_lock_minutes > 0:
            self._start_auto_lock_monitor()

        logger.info(f"Authentification initialisée - Verrouillage: {lock_enabled}, "
                   f"Auto-lock: {auto_lock_minutes}min")

    def set_lock_callback(self, callback: Callable[[], None]) -> None:
        """
        Définit la fonction à appeler lors du verrouillage.

        Args:
            callback: Fonction à appeler
        """
        self._lock_callback = callback

    def _start_auto_lock_monitor(self) -> None:
        """Démarre le moniteur de verrouillage automatique."""
        if self._auto_lock_thread is not None and self._auto_lock_thread.is_alive():
            return

        self._stop_auto_lock.clear()
        self._auto_lock_thread = threading.Thread(
            target=self._auto_lock_monitor,
            daemon=True
        )
        self._auto_lock_thread.start()
        logger.debug("Moniteur de verrouillage automatique démarré")

    def _stop_auto_lock_monitor(self) -> None:
        """Arrête le moniteur de verrouillage automatique."""
        if self._auto_lock_thread is not None:
            self._stop_auto_lock.set()
            self._auto_lock_thread.join(timeout=2.0)
            self._auto_lock_thread = None
            logger.debug("Moniteur de verrouillage automatique arrêté")

    def _auto_lock_monitor(self) -> None:
        """Thread de surveillance pour le verrouillage automatique."""
        while not self._stop_auto_lock.is_set():
            if self.should_auto_lock():
                self.lock()

            # Vérifier toutes les 30 secondes
            self._stop_auto_lock.wait(30)

    def update_activity(self) -> None:
        """Met à jour le timestamp de dernière activité."""
        self.last_activity = datetime.now()
        logger.debug("Activité mise à jour")

    def should_auto_lock(self) -> bool:
        """
        Vérifie si l'application devrait se verrouiller automatiquement.

        Returns:
            True si le verrouillage automatique doit être activé
        """
        if not self.lock_enabled or self.auto_lock_minutes <= 0 or self.is_locked:
            return False

        time_since_activity = datetime.now() - self.last_activity
        threshold = timedelta(minutes=self.auto_lock_minutes)

        return time_since_activity >= threshold

    def lock(self) -> None:
        """Verrouille l'application."""
        if not self.lock_enabled or self.is_locked:
            return

        self.is_locked = True
        logger.info("Application verrouillée")

        if self._lock_callback:
            self._lock_callback()

    def unlock(self, password: Optional[str] = None) -> bool:
        """
        Déverrouille l'application.

        Args:
            password: Mot de passe

        Returns:
            True si le déverrouillage a réussi
        """
        if not self.is_locked:
            return True

        # Vérifier le mot de passe si défini
        if self.has_password():
            if not password:
                logger.warning("Mot de passe requis mais non fourni")
                return False

            authenticated = self.verify_password(password)
        else:
            # Pas de mot de passe défini, authentification système basique
            authenticated = self._authenticate_system(password)

        if authenticated:
            self.is_locked = False
            self.update_activity()
            logger.info("Application déverrouillée")
            return True

        logger.warning("Échec de l'authentification")
        return False

    def _authenticate_system(self, password: Optional[str] = None) -> bool:
        """
        Authentifie l'utilisateur via le système.

        Args:
            password: Mot de passe optionnel

        Returns:
            True si authentifié

        Note:
            Implémentation simplifiée. Pour une sécurité accrue, utiliser:
            - Windows: DPAPI, Credential Manager, ou Windows Hello
            - Linux: PAM, polkit, ou GNOME Keyring
        """
        # Si app_lock_enabled mais pas de mot de passe défini,
        # on considère simplement le verrouillage comme visuel
        return True

    def enable_lock(self, enable: bool = True) -> None:
        """
        Active ou désactive le verrouillage de l'application.

        Args:
            enable: Active si True, désactive si False
        """
        self.lock_enabled = enable
        logger.info(f"Verrouillage {'activé' if enable else 'désactivé'}")

    def set_auto_lock_minutes(self, minutes: int) -> None:
        """
        Définit le délai de verrouillage automatique.

        Args:
            minutes: Délai en minutes (0 = désactivé)
        """
        old_value = self.auto_lock_minutes
        self.auto_lock_minutes = max(0, minutes)

        # Redémarrer le moniteur si nécessaire
        if old_value == 0 and minutes > 0:
            self._start_auto_lock_monitor()
        elif minutes == 0:
            self._stop_auto_lock_monitor()

        logger.info(f"Verrouillage automatique défini à {minutes} minutes")

    def get_time_until_lock(self) -> Optional[timedelta]:
        """
        Calcule le temps restant avant le verrouillage automatique.

        Returns:
            Temps restant, ou None si le verrouillage automatique est désactivé
        """
        if not self.lock_enabled or self.auto_lock_minutes <= 0:
            return None

        time_since_activity = datetime.now() - self.last_activity
        threshold = timedelta(minutes=self.auto_lock_minutes)
        remaining = threshold - time_since_activity

        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def cleanup(self) -> None:
        """Nettoie les ressources (thread d'auto-verrouillage)."""
        self._stop_auto_lock_monitor()
        logger.debug("Gestionnaire d'authentification nettoyé")


# Instance globale
_auth_manager: Optional[AuthenticationManager] = None


def get_auth_manager(
    lock_enabled: bool = False,
    auto_lock_minutes: int = 0
) -> AuthenticationManager:
    """
    Récupère l'instance globale du gestionnaire d'authentification.

    Args:
        lock_enabled: Active le verrouillage (utilisé uniquement lors de l'initialisation)
        auto_lock_minutes: Délai d'auto-verrouillage (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du gestionnaire d'authentification
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager(lock_enabled, auto_lock_minutes)
    return _auth_manager

