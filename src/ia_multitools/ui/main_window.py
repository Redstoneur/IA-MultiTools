"""
Fenêtre principale de l'application IA-MultiTools.

Contient la navigation par onglets et les menus principaux.
"""

import logging
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Optional
from pathlib import Path
import sys

from ..core.config_manager import ConfigManager
from ..core.authentication import AuthenticationManager
from ..constants import APP_FULL_NAME, APP_LICENSE
from .tabs.definition_tab import DefinitionTab
from .tabs.synonym_tab import SynonymTab
from .tabs.correction_tab import CorrectionTab
from .tabs.email_tab import EmailTab
from .tabs.translation_tab import TranslationTab
from .settings_window import SettingsWindow
from .first_run_wizard import FirstRunWizard

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Fenêtre principale de l'application.

    Gère l'interface utilisateur principale avec navigation par onglets.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        auth_manager: AuthenticationManager,
        debug_mode: bool = False
    ) -> None:
        """
        Initialise la fenêtre principale.

        Args:
            config_manager: Gestionnaire de configuration
            auth_manager: Gestionnaire d'authentification
            debug_mode: Mode debug
        """
        self.config_manager = config_manager
        self.auth_manager = auth_manager
        self.debug_mode = debug_mode
        self.config = config_manager.get_config()

        # Créer la fenêtre principale
        self.root = ttk.Window(
            title="IA-MultiTools",
            themename=self.config.appearance.theme
        )

        width = min(1000, self.root.winfo_screenwidth() - 80)
        height = min(700, self.root.winfo_screenheight() - 100)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(min(800, width), min(400, height))

        self.logo_image: Optional[tk.PhotoImage] = None
        self._setup_branding()

        # Variables
        self.settings_window: Optional[SettingsWindow] = None

        # Construire l'interface
        self._build_menu()
        self._build_ui()

        # Gérer la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Gérer l'activité pour le verrouillage automatique
        self.root.bind("<Key>", lambda e: self.auth_manager.update_activity())
        self.root.bind("<Button>", lambda e: self.auth_manager.update_activity())

        logger.info("Fenêtre principale créée")

        # Afficher l'assistant de premier lancement si nécessaire
        if self.config.first_run:
            logger.info("Premier lancement détecté, affichage de l'assistant")
            self.root.after(500, self._show_first_run_wizard)

    def _resolve_asset_path(self, filename: str) -> Optional[Path]:
        """Résout le chemin d'un asset en mode dev et en mode PyInstaller."""
        candidate_dirs = []
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidate_dirs.append(Path(sys._MEIPASS) / "assets")

        candidate_dirs.extend([
            Path(__file__).resolve().parents[3] / "assets",
            Path.cwd() / "assets",
        ])

        for directory in candidate_dirs:
            candidate = directory / filename
            if candidate.exists():
                return candidate
        return None

    def _setup_branding(self) -> None:
        """Charge et applique le logo/icône de l'application si disponible."""
        logo_path = self._resolve_asset_path("logo.png")
        if not logo_path:
            logger.warning("Logo non trouvé dans assets/logo.png")
            return
        try:
            self.logo_image = tk.PhotoImage(file=str(logo_path)).subsample(4, 4)
            logo_image = self.logo_image
            if logo_image is not None:
                self.root.iconphoto(True, logo_image)
            logger.info(f"Logo chargé: {logo_path}")
        except Exception as exc:
            logger.warning(f"Impossible de charger le logo: {exc}")

    def _build_menu(self) -> None:
        """Construit la barre de menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Paramètres", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_closing)

        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Historique", command=self._show_history)
        tools_menu.add_command(label="Tester la connexion IA", command=self._test_ai_connection)

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)

    def _build_ui(self) -> None:
        """Construit l'interface utilisateur principale."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, padx=5, pady=(0, 10))

        if self.logo_image:
            ttk.Label(header_frame, image=self.logo_image).pack(side=LEFT, padx=(0, 8))

        title_label = ttk.Label(
            header_frame,
            text="IA-MultiTools",
            font=(self.config.appearance.font_family, 18, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(side=LEFT)

        # Bouton paramètres
        settings_btn = ttk.Button(
            header_frame,
            text="⚙ Paramètres",
            command=self._open_settings,
            bootstyle=SECONDARY
        )
        settings_btn.pack(side=RIGHT, padx=5)

        # Séparateur
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=5)

        # Notebook (onglets)
        self.notebook = ttk.Notebook(main_frame, bootstyle=PRIMARY)
        self.notebook.pack(fill=BOTH, expand=YES, pady=5)

        # Créer les onglets
        self._create_tabs()

    def _create_tabs(self) -> None:
        """Crée tous les onglets de l'application."""
        # Onglet Définition
        self.definition_tab = DefinitionTab(self.notebook, self.config_manager)
        self.notebook.add(self.definition_tab.frame.container, text="📖 Définition")

        # Onglet Synonymes
        self.synonym_tab = SynonymTab(self.notebook, self.config_manager)
        self.notebook.add(self.synonym_tab.frame.container, text="🔄 Synonymes")

        # Onglet Correction de texte
        self.correction_tab = CorrectionTab(self.notebook, self.config_manager)
        self.notebook.add(self.correction_tab.frame.container, text="✏️ Correction")

        # Onglet E-mails
        self.email_tab = EmailTab(self.notebook, self.config_manager)
        self.notebook.add(self.email_tab.frame.container, text="📧 E-mails")
        self.translation_tab = TranslationTab(self.notebook, self.config_manager)
        self.notebook.add(self.translation_tab.frame.container, text="Traduction")

        logger.debug("Tous les onglets ont été créés")

    def _open_settings(self) -> None:
        """Ouvre la fenêtre de paramètres."""
        if self.settings_window is None or not self.settings_window.window.winfo_exists():
            self.settings_window = SettingsWindow(self.root, self.config_manager)
        else:
            self.settings_window.window.lift()
            self.settings_window.window.focus()

    def _show_history(self) -> None:
        """Affiche l'historique."""
        from ..core.history_manager import get_history_manager

        history = get_history_manager()
        stats = history.get_statistics()

        info_text = f"""Statistiques de l'historique:

Total d'entrées: {stats['total_entries']}

Utilisation par outil:
"""
        for tool, count in stats.get('tools_usage', {}).items():
            info_text += f"  • {tool}: {count}\n"

        if stats['oldest_entry']:
            info_text += f"\nEntrée la plus ancienne: {stats['oldest_entry']}"
        if stats['newest_entry']:
            info_text += f"\nEntrée la plus récente: {stats['newest_entry']}"

        messagebox.showinfo("Historique", info_text)

    def _test_ai_connection(self) -> None:
        """Teste la connexion à l'API IA."""
        from ..core.openai_client import get_openai_client

        try:
            client = get_openai_client()
            success, message = client.test_connection()

            if success:
                messagebox.showinfo("Test de connexion", "✓ " + message)
            else:
                messagebox.showerror("Test de connexion", "✗ " + message)
        except Exception as e:
            messagebox.showerror("Test de connexion", f"Erreur: {str(e)}")

    def _show_about(self) -> None:
        """Affiche la boîte de dialogue À propos."""
        about_text = f"""{APP_FULL_NAME}

Application desktop Python multiplateforme proposant
plusieurs outils linguistiques assistés par IA.

Outils disponibles:
  • Définition de mots et concepts
  • Synonymes et antonymes
  • Correction de texte
  • Correction d'e-mails professionnels

Licence: {APP_LICENSE}
© 2026 IA-MultiTools Team
"""
        messagebox.showinfo("À propos", about_text)

    def _show_documentation(self) -> None:
        """Ouvre la documentation."""
        import webbrowser
        doc_url = "https://github.com/votre-username/IA-MultiTools/blob/main/README_FULL.md"

        try:
            webbrowser.open(doc_url)
        except:
            messagebox.showinfo(
                "Documentation",
                f"Consultez la documentation à:\n{doc_url}"
            )

    def _on_closing(self) -> None:
        """Gère la fermeture de la fenêtre."""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            logger.info("Fermeture de l'application demandée par l'utilisateur")
            self.root.quit()
            self.root.destroy()

    def _show_first_run_wizard(self) -> None:
        """Affiche l'assistant de premier lancement."""
        try:
            FirstRunWizard(self.root, self.config_manager)
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de l'assistant de premier lancement: {e}")
            messagebox.showerror(
                "Erreur",
                "Impossible d'ouvrir l'assistant de configuration.\n"
                "Vous pouvez configurer l'application via le menu Paramètres."
            )

    def run(self) -> None:
        """Lance la boucle principale de l'application."""
        logger.info("Démarrage de la boucle principale")
        self.root.mainloop()
