"""
Constantes de l'application IA-MultiTools.

Ce fichier contient les valeurs fixes qui ne doivent JAMAIS être modifiées
automatiquement par le code. Toute modification doit être explicite.
"""

# Version de l'application
# ⚠️ NE PAS MODIFIER AUTOMATIQUEMENT
# La version doit être changée manuellement uniquement lors de releases validées
__version__ = "1.0.0"
VERSION = "1.0.0"
VERSION_LOCKED = True  # Flag pour empêcher toute modification automatique

# Informations de l'application
APP_NAME = "IA-MultiTools"
APP_FULL_NAME = f"{APP_NAME} v{VERSION}"
APP_AUTHOR = "IA-MultiTools Team"
APP_LICENSE = "GNU GPL v3.0 (GPL-3.0-only)"
APP_YEAR = 2026

# Configuration par défaut
DEFAULT_AI_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_AI_MODEL = "meta-llama-3.1-8b-instruct"
DEFAULT_AI_TEMPERATURE = 0.2
DEFAULT_AI_TIMEOUT = 60
DEFAULT_AI_MAX_TOKENS = 2000

# Sécurité
MIN_PASSWORD_LENGTH = 4
PBKDF2_ITERATIONS = 100000
SALT_LENGTH = 16

# Logging
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_NAME = "ia_multitools.log"
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Chemins
CONFIG_FILE_NAME = "config.enc"
HISTORY_FILE_NAME = "history.enc"
PROMPTS_FILE_NAME = "prompts.enc"
CACHE_FILE_NAME = "cache.enc"

# Comportements
ALLOW_AUTO_VERSION_BUMP = False  # ⚠️ TOUJOURS False en production
ALLOW_AUTO_DOCUMENTATION = False  # Pas de génération auto de fichiers .md
ENABLE_TELEMETRY = False  # Pas de télémétrie
ENABLE_AUTO_UPDATE = False  # Pas de mise à jour automatique

# Validation
def get_version() -> str:
    """
    Retourne la version de l'application.

    Returns:
        Version au format string
    """
    if VERSION_LOCKED:
        # Version verrouillée, retour de la constante
        return VERSION
    else:
        # En développement uniquement, peut être dynamique
        return __version__

def validate_version_lock() -> bool:
    """
    Vérifie que la version est bien verrouillée.

    Returns:
        True si la version est verrouillée
    """
    return VERSION_LOCKED and VERSION == "1.0.0"
