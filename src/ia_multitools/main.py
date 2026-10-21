"""
Point d'entrée principal de l'application IA-MultiTools.

Lance l'application avec toutes ses dépendances et configuration.
"""

import sys
import argparse
import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from .constants import APP_FULL_NAME

# Configuration du logging avant tout import
def setup_logging(debug_mode: bool = False) -> None:
    """
    Configure le système de logging.

    Args:
        debug_mode: Active le mode debug avec plus de détails
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Créer le dossier de logs
    if debug_mode:
        log_dir = Path("logs")
    else:
        import platformdirs
        log_dir = Path(platformdirs.user_log_dir("IA-MultiTools", "IA-MultiTools"))

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "ia_multitools.log"

    # Configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("IA-MultiTools - Démarrage de l'application")
    logger.info(f"Mode debug: {debug_mode}")
    logger.info(f"Fichier de logs: {log_file}")
    logger.info("="*60)


def parse_arguments() -> argparse.Namespace:
    """
    Parse les arguments de ligne de commande.

    Returns:
        Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="IA-MultiTools - Outils linguistiques assistés par IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python -m src.ia_multitools.main
  python -m src.ia_multitools.main --debug
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Active le mode debug (logs détaillés, stockage local)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=APP_FULL_NAME
    )

    return parser.parse_args()


def check_dependencies() -> tuple[bool, list[str]]:
    """
    Vérifie que toutes les dépendances sont installées.

    Returns:
        Tuple (toutes_présentes, liste_manquantes)
    """
    required_packages = [
        'openai',
        'cryptography',
        'keyring',
        'ttkbootstrap',
        'platformdirs',
        'dotenv'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    return len(missing) == 0, missing


def main() -> int:
    """
    Fonction principale de l'application.

    Returns:
        Code de sortie (0 = succès, 1 = erreur)
    """
    # Parser les arguments
    args = parse_arguments()

    # Configurer le logging
    setup_logging(debug_mode=args.debug)
    logger = logging.getLogger(__name__)

    try:
        # Vérifier les dépendances
        logger.info("Vérification des dépendances...")
        all_present, missing = check_dependencies()

        if not all_present:
            error_msg = (
                f"Dépendances manquantes: {', '.join(missing)}\n\n"
                f"Installez-les avec:\npip install {' '.join(missing)}"
            )
            logger.error(error_msg)

            # Si possible, afficher une boîte de dialogue
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Dépendances manquantes", error_msg)
                root.destroy()
            except:
                pass

            return 1

        logger.info("Toutes les dépendances sont présentes")

        # Importer les modules après vérification des dépendances
        # Support pour exécution directe ET via module
        try:
            # Essayer imports relatifs (python -m)
            from .core.config_manager import get_config_manager
            from .core.authentication import get_auth_manager
            from .core.openai_client import init_openai_client
            from .ui.main_window import MainWindow
        except ImportError:
            # Fallback sur imports absolus (exécution directe)
            import sys
            from pathlib import Path
            # Ajouter le dossier src au path
            src_path = Path(__file__).parent.parent.parent
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))

            from ia_multitools.core.config_manager import get_config_manager
            from ia_multitools.core.authentication import get_auth_manager
            from ia_multitools.core.openai_client import init_openai_client
            from ia_multitools.ui.main_window import MainWindow

        logger.info("Initialisation de la configuration...")

        # Initialiser la configuration
        config_manager = get_config_manager(debug_mode=args.debug)
        config = config_manager.get_config()

        # Initialiser l'authentification
        logger.info("Initialisation de l'authentification...")
        auth_manager = get_auth_manager(
            lock_enabled=config.security.app_lock_enabled,
            auto_lock_minutes=config.security.auto_lock_minutes
        )

        # Demander le mot de passe au démarrage si nécessaire
        if config.security.app_lock_enabled and auth_manager.has_password():
            logger.info("Sécurité activée, demande de mot de passe...")
            from ia_multitools.ui.password_dialog import PasswordDialog

            dialog = PasswordDialog(
                parent=None,
                auth_manager=auth_manager,
                is_startup=True
            )

            authenticated = dialog.wait()

            if not authenticated:
                logger.warning("Authentification échouée, arrêt de l'application")
                return 1

        # Initialiser le client OpenAI
        logger.info("Initialisation du client OpenAI...")
        try:
            init_openai_client(
                api_key=config.ai.api_key or "sk-dummy",
                base_url=config.ai.base_url,
                model=config.ai.model,
                temperature=config.ai.temperature,
                max_tokens=config.ai.max_tokens,
                timeout=config.ai.timeout,
                verify_ssl=config.ai.verify_ssl
            )
        except Exception as e:
            logger.warning(f"Impossible d'initialiser le client OpenAI: {e}")
            logger.warning("L'application démarrera sans connexion IA (à configurer)")

        # Lancer l'interface graphique
        logger.info("Lancement de l'interface graphique...")

        app = MainWindow(config_manager, auth_manager, debug_mode=args.debug)

        logger.info("Application prête")
        app.run()

        # Nettoyage
        logger.info("Arrêt de l'application...")
        auth_manager.cleanup()

        logger.info("Application fermée proprement")
        return 0

    except KeyboardInterrupt:
        logger.info("Application interrompue par l'utilisateur")
        return 0
    except Exception as e:
        logger.exception(f"Erreur fatale: {e}")

        # Afficher une boîte de dialogue si possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Erreur fatale",
                f"Une erreur inattendue s'est produite:\n\n{str(e)}\n\n"
                f"Consultez les logs pour plus de détails."
            )
            root.destroy()
        except:
            pass

        return 1


if __name__ == "__main__":
    sys.exit(main())
