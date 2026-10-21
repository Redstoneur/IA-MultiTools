"""
Gestionnaire de configuration de l'application.

Ce module gère la configuration de l'application, incluant les paramètres d'IA,
de sécurité, d'apparence et les prompts système.
"""

import os
from pathlib import Path
from typing import Any, Optional
import logging
from dataclasses import dataclass, field, asdict
import sys
import platformdirs

from .keyring_manager import KeyringManager, get_keyring_manager
from ..constants import VERSION, ALLOW_AUTO_VERSION_BUMP

logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """Configuration de l'API OpenAI."""
    api_key: str = ""
    base_url: str = "http://127.0.0.1:1234/v1"
    model: str = "meta-llama-3.1-8b-instruct"
    temperature: float = 0.2
    timeout: int = 60
    verify_ssl: bool = True
    max_tokens: Optional[int] = None


@dataclass
class SecurityConfig:
    """Configuration de sécurité."""
    encryption_enabled: bool = True
    use_keyring: bool = True
    app_lock_enabled: bool = False
    auto_lock_minutes: int = 0  # 0 = désactivé


@dataclass
class AppearanceConfig:
    """Configuration de l'apparence."""
    theme: str = "darkly"  # ttkbootstrap theme
    font_size: int = 11
    font_family: str = "Segoe UI"


@dataclass
class HistoryConfig:
    """Configuration de l'historique."""
    enabled: bool = True
    max_entries: int = 1000
    auto_cleanup_days: int = 90


@dataclass
class LoggingConfig:
    """Configuration du logging."""
    enabled: bool = True
    level: str = "INFO"
    rotation: bool = True
    max_size_mb: int = 10
    backup_count: int = 5


@dataclass
class SystemPrompts:
    """Prompts système pour chaque outil."""
    definition: str = field(default=(
        "Tu es un assistant spécialisé dans les définitions. "
        "Fournis une définition claire, concise et précise du terme demandé. "
        "Ne fournis aucune information supplémentaire, seulement la définition."
    ))

    synonym: str = field(default=(
        "Tu es un assistant spécialisé dans les synonymes et antonymes. "
        "Fournis uniquement une liste de mots, sans explications, sans numérotation, "
        "séparés par des virgules. Ne fournis aucune autre information."
    ))

    text_correction: str = field(default=(
        "Tu es un correcteur professionnel. Corrige l'orthographe, la grammaire "
        "et améliore le style du texte fourni. Respecte les instructions embarquées "
        "entre <instruction> et </instruction>. Retourne uniquement le texte corrigé, "
        "sans commentaires ni explications."
    ))

    email_correction: str = field(default=(
        "Tu es un assistant de rédaction d'e-mails professionnels. "
        "Corrige et améliore le contenu fourni pour en faire un e-mail professionnel. "
        "Respecte les instructions embarquées entre <instruction> et </instruction>. "
        "Retourne uniquement l'e-mail final, sans commentaires ni explications."
    ))


@dataclass
class AppConfig:
    """Configuration complète de l'application."""
    ai: AIConfig = field(default_factory=AIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    appearance: AppearanceConfig = field(default_factory=AppearanceConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    prompts: SystemPrompts = field(default_factory=SystemPrompts)

    # Métadonnées
    version: str = VERSION  # Version verrouillée depuis constants
    first_run: bool = True


class ConfigManager:
    """
    Gestionnaire de configuration de l'application.

    Gère le chargement, la sauvegarde et la validation de la configuration.
    Utilise le stockage sécurisé pour les données sensibles.
    """

    CONFIG_FILENAME = "config"
    API_KEY_KEYRING_ID = "openai_api_key"
    APP_LOCK_PASSWORD_KEYRING_ID = "app_lock_password"

    def __init__(self, debug_mode: bool = False) -> None:
        """
        Initialise le gestionnaire de configuration.

        Args:
            debug_mode: Si True, utilise le dossier de l'application au lieu du dossier utilisateur
        """
        self.debug_mode = debug_mode
        self.config_dir = self._get_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Initialiser le stockage sécurisé
        from .secure_storage import init_secure_storage
        self.storage = init_secure_storage(self.config_dir)
        self.keyring_manager: KeyringManager = get_keyring_manager()

        self.config = AppConfig()
        self._load_env_variables()

        logger.info(f"Gestionnaire de configuration initialisé: {self.config_dir}")

    def _get_config_dir(self) -> Path:
        """
        Détermine le répertoire de configuration.

        Returns:
            Chemin du répertoire de configuration
        """
        if self.debug_mode:
            # Mode debug: dossier de l'application
            if getattr(sys, 'frozen', False):
                # Si exécutable PyInstaller
                app_dir = Path(sys.executable).parent
            else:
                # Si script Python
                app_dir = Path(__file__).parent.parent.parent.parent
            config_dir = app_dir / "data"
            logger.debug(f"Mode debug: utilisation du dossier application: {config_dir}")
            return config_dir
        else:
            # Mode production: dossier utilisateur
            config_dir = Path(platformdirs.user_config_dir("IA-MultiTools", "IA-MultiTools"))
            logger.debug(f"Mode production: utilisation du dossier utilisateur: {config_dir}")
            return config_dir

    def _load_env_variables(self) -> None:
        """
        Charge les variables d'environnement dans la configuration.
        """
        from dotenv import load_dotenv
        load_dotenv()

        # Charger les variables d'environnement
        if api_key := os.getenv("OPENAI_API_KEY"):
            self.config.ai.api_key = api_key
        if base_url := os.getenv("OPENAI_BASE_URL"):
            self.config.ai.base_url = base_url
        if model := os.getenv("OPENAI_MODEL"):
            self.config.ai.model = model
        if temperature := os.getenv("OPENAI_TEMPERATURE"):
            try:
                self.config.ai.temperature = float(temperature)
            except ValueError:
                logger.warning(f"OPENAI_TEMPERATURE invalide: {temperature}")
        if timeout := os.getenv("OPENAI_TIMEOUT"):
            try:
                self.config.ai.timeout = int(timeout)
            except ValueError:
                logger.warning(f"OPENAI_TIMEOUT invalide: {timeout}")
        if verify_ssl := os.getenv("OPENAI_VERIFY_SSL"):
            self.config.ai.verify_ssl = verify_ssl.lower() in ("true", "1", "yes")

        logger.debug("Variables d'environnement chargées")

    def load(self) -> bool:
        """
        Charge la configuration depuis le fichier chiffré.

        Returns:
            True si le chargement a réussi
        """
        try:
            data = self.storage.load_encrypted(self.CONFIG_FILENAME)

            if data is None:
                logger.info("Aucune configuration trouvée, utilisation des valeurs par défaut")
                return False

            # Reconstruire la configuration
            ai_data = data.get("ai", {})
            # La clé API n'est jamais restaurée depuis le fichier config.
            ai_data.pop("api_key", None)
            self.config.ai = AIConfig(**ai_data)
            self.config.security = SecurityConfig(**data.get("security", {}))
            self.config.appearance = AppearanceConfig(**data.get("appearance", {}))
            self.config.history = HistoryConfig(**data.get("history", {}))
            self.config.logging = LoggingConfig(**data.get("logging", {}))
            self.config.prompts = SystemPrompts(**data.get("prompts", {}))

            # Restaurer la clé API depuis le trousseau si activé.
            if self.config.security.use_keyring and self.keyring_manager.is_available():
                self.config.ai.api_key = self.keyring_manager.get_api_key() or ""
            else:
                self.config.ai.api_key = ""

            # Charger la version avec protection
            loaded_version = data.get("version", VERSION)
            if not ALLOW_AUTO_VERSION_BUMP and loaded_version != VERSION:
                logger.warning(
                    f"Version dans config ({loaded_version}) != VERSION verrouillée ({VERSION}). "
                    f"Forçage à {VERSION}"
                )
                self.config.version = VERSION
            else:
                self.config.version = loaded_version

            self.config.first_run = data.get("first_run", False)

            # Les variables d'environnement gardent la priorité sur les valeurs persistées.
            self._load_env_variables()

            logger.info("Configuration chargée avec succès")
            return True

        except Exception as e:
            logger.error("Erreur lors du chargement de la configuration: %s", type(e).__name__)
            return False

    def save(self) -> bool:
        """
        Sauvegarde la configuration dans un fichier chiffré.

        Returns:
            True si la sauvegarde a réussi
        """
        try:
            if not self.keyring_manager.is_available():
                logger.error("Le trousseau système est indisponible; configuration non sauvegardée")
                return False
            if not self.config.security.use_keyring:
                logger.error("Le trousseau système est obligatoire pour sauvegarder la configuration")
                return False

            api_key = self.config.ai.api_key
            if api_key:
                if not self.keyring_manager.is_available():
                    logger.error("Le trousseau système est requis pour stocker la clé API, mais il est indisponible")
                    return False
                if not self.keyring_manager.set_api_key(api_key):
                    logger.error("Impossible de stocker la clé API dans le trousseau système")
                    return False
            elif self.keyring_manager.is_available() and not self.keyring_manager.delete_api_key():
                logger.error("Impossible de supprimer la clé API du trousseau système")
                return False

            ai_data = asdict(self.config.ai)
            ai_data.pop("api_key", None)

            data = {
                "ai": ai_data,
                "security": asdict(self.config.security),
                "appearance": asdict(self.config.appearance),
                "history": asdict(self.config.history),
                "logging": asdict(self.config.logging),
                "prompts": asdict(self.config.prompts),
                "version": self.config.version,
                "first_run": self.config.first_run
            }

            success = self.storage.save_encrypted(self.CONFIG_FILENAME, data)

            if success:
                logger.info("Configuration sauvegardée avec succès")
            else:
                logger.error("Échec de la sauvegarde de la configuration")

            return success

        except Exception as e:
            logger.error("Erreur lors de la sauvegarde de la configuration: %s", type(e).__name__)
            return False

    def reset_to_defaults(self) -> None:
        """Réinitialise la configuration aux valeurs par défaut."""
        self.config = AppConfig()
        logger.info("Configuration réinitialisée aux valeurs par défaut")

    def get_config(self) -> AppConfig:
        """
        Récupère la configuration actuelle.

        Returns:
            Configuration de l'application
        """
        return self.config

    def update_ai_config(self, **kwargs: Any) -> None:
        """
        Met à jour la configuration IA.

        Args:
            **kwargs: Paramètres à mettre à jour
        """
        for key, value in kwargs.items():
            if hasattr(self.config.ai, key):
                setattr(self.config.ai, key, value)
                sensitive = any(
                    marker in key.lower()
                    for marker in ("api_key", "password", "secret", "token", "credential")
                )
                safe_value = "[REDACTED]" if sensitive else value
                logger.debug(f"Configuration IA mise à jour: {key}={safe_value}")

    # Alias de compatibilité utilisés par l'UI.
    def load_config(self) -> bool:
        """Alias de `load` pour compatibilité API interne."""
        return self.load()

    def save_config(self) -> bool:
        """Alias de `save` pour compatibilité API interne."""
        return self.save()

    def set_password(self, password: str) -> bool:
        """Délègue la gestion du mot de passe au gestionnaire d'authentification."""
        from .authentication import get_auth_manager
        return get_auth_manager().set_password(password)

    def verify_password(self, password: str) -> bool:
        """Délègue la vérification du mot de passe au gestionnaire d'authentification."""
        from .authentication import get_auth_manager
        return get_auth_manager().verify_password(password)

    def has_password(self) -> bool:
        """Indique si un mot de passe d'application est défini."""
        from .authentication import get_auth_manager
        return get_auth_manager().has_password()

    def remove_password(self) -> bool:
        """Supprime le mot de passe d'application."""
        from .authentication import get_auth_manager
        return get_auth_manager().remove_password()

    def update_security_config(self, **kwargs: Any) -> None:
        """
        Met à jour la configuration de sécurité.

        Args:
            **kwargs: Paramètres à mettre à jour
        """
        for key, value in kwargs.items():
            if hasattr(self.config.security, key):
                setattr(self.config.security, key, value)
                safe_value = (
                    "[REDACTED]"
                    if any(marker in key.lower() for marker in ("password", "secret", "token", "credential"))
                    else value
                )
                logger.debug(f"Configuration sécurité mise à jour: {key}={safe_value}")

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valide la configuration actuelle.

        Returns:
            Tuple (valide, liste_erreurs)
        """
        errors = []

        # Validation IA
        if not self.config.ai.base_url:
            errors.append("URL de base de l'API non définie")
        if not self.config.ai.model:
            errors.append("Modèle IA non défini")
        if not (0.0 <= self.config.ai.temperature <= 2.0):
            errors.append("Température doit être entre 0.0 et 2.0")
        if self.config.ai.timeout <= 0:
            errors.append("Timeout doit être positif")

        # Validation sécurité
        if not self.config.security.encryption_enabled:
            errors.append("Le chiffrement des données ne peut pas être désactivé")
        if not self.config.security.use_keyring:
            errors.append("Le trousseau système est obligatoire pour le stockage sécurisé")
        if self.config.security.auto_lock_minutes < 0:
            errors.append("Délai de verrouillage automatique doit être >= 0")

        # Validation historique
        if self.config.history.max_entries <= 0:
            errors.append("Nombre max d'entrées d'historique doit être > 0")

        is_valid = len(errors) == 0
        return is_valid, errors


# Instance globale
_config_manager: Optional[ConfigManager] = None


def get_config_manager(debug_mode: bool = False) -> ConfigManager:
    """
    Récupère l'instance globale du gestionnaire de configuration.

    Args:
        debug_mode: Mode debug (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du gestionnaire de configuration
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(debug_mode)
        _config_manager.load()
    return _config_manager
