"""
Assistant de configuration initiale au premier lancement.
"""

import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Any, Optional, Callable

from ..core.config_manager import ConfigManager
from ..core.openai_client import OpenAIClient, get_openai_client

logger = logging.getLogger(__name__)


class FirstRunWizard:
    """Assistant de configuration au premier lancement."""

    def __init__(self, parent: Any, config_manager: ConfigManager, on_complete: Optional[Callable] = None) -> None:
        """
        Initialise l'assistant de premier lancement.

        Args:
            parent: Widget parent
            config_manager: Gestionnaire de configuration
            on_complete: Callback appelé àla fin de la configuration
        """
        self.config_manager = config_manager
        self.on_complete = on_complete

        # Fenêtre modale
        self.window = ttk.Toplevel(parent)
        self.window.title("🚀 Configuration initiale - IA-MultiTools")
        self.window.geometry("700x550")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # Centrer la fenêtre
        self._center_window()

        self._build_ui()

        logger.info("Assistant de premier lancement ouvert")

    def _center_window(self) -> None:
        """Centre la fenêtre sur l'écran."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _build_ui(self) -> None:
        """Construit l'interface de l'assistant."""
        # Conteneur principal
        main_frame = ttk.Frame(self.window, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            header_frame,
            text="🎉 Bienvenue dans IA-MultiTools !",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor=W)

        ttk.Label(
            header_frame,
            text="Configurons votre connexion IA pour commencer",
            font=("Segoe UI", 11)
        ).pack(anchor=W, pady=(5, 0))

        # Séparateur
        ttk.Separator(main_frame).pack(fill=X, pady=15)

        # Section configuration
        config_frame = ttk.Labelframe(main_frame, text="Configuration de l'IA", padding=15)
        config_frame.pack(fill=BOTH, expand=YES, pady=(0, 15))

        # URL de base
        ttk.Label(config_frame, text="URL de base de votre API:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        ttk.Label(
            config_frame,
            text="Exemples: http://localhost:1234/v1 (LM Studio), http://localhost:8080/v1 (LocalAI)",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack(anchor=W, pady=(0, 5))

        self.base_url_entry = ttk.Entry(config_frame, font=("Segoe UI", 10))
        self.base_url_entry.insert(0, "http://127.0.0.1:1234/v1")
        self.base_url_entry.pack(fill=X, pady=(0, 15))

        # Clé API
        ttk.Label(config_frame, text="Clé API (optionnel pour serveurs locaux):", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        self.api_key_entry = ttk.Entry(config_frame, font=("Segoe UI", 10), show="*")
        self.api_key_entry.insert(0, "sk-dummy")
        self.api_key_entry.pack(fill=X, pady=(0, 15))

        # Modèle
        ttk.Label(config_frame, text="Nom du modèle:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        self.model_entry = ttk.Entry(config_frame, font=("Segoe UI", 10))
        self.model_entry.insert(0, "meta-llama-3.1-8b-instruct")
        self.model_entry.pack(fill=X, pady=(0, 15))

        # Zone de statut
        self.status_label = ttk.Label(
            config_frame,
            text="",
            font=("Segoe UI", 9),
            bootstyle=INFO
        )
        self.status_label.pack(fill=X, pady=10)

        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X)

        self.test_btn = ttk.Button(
            button_frame,
            text="🔍 Tester la connexion",
            command=self._test_connection,
            bootstyle=INFO,
            width=25
        )
        self.test_btn.pack(side=LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(
            button_frame,
            text="✓ Enregistrer et continuer",
            command=self._save_and_continue,
            bootstyle=SUCCESS,
            width=25,
            state="disabled"
        )
        self.save_btn.pack(side=LEFT)

        ttk.Button(
            button_frame,
            text="Ignorer (configurer plus tard)",
            command=self._skip,
            bootstyle=SECONDARY,
            width=25
        ).pack(side=RIGHT)

        # Instructions
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=X, pady=(15, 0))

        ttk.Label(
            info_frame,
            text="💡 Astuce: Vous pouvez toujours modifier ces paramètres via le menu Paramètres.",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack()

    def _test_connection(self) -> None:
        """Teste la connexion à l'API."""
        base_url = self.base_url_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        model = self.model_entry.get().strip()

        if not base_url:
            messagebox.showerror("Erreur", "Veuillez entrer l'URL de base.")
            return

        if not model:
            messagebox.showerror("Erreur", "Veuillez entrer le nom du modèle.")
            return

        # Désactiver les boutons pendant le test
        self.test_btn.config(state="disabled", text="⏳ Test en cours...")
        self.save_btn.config(state="disabled")
        self.status_label.config(text="Test de connexion en cours...", bootstyle=INFO)

        self.window.update()

        try:
            # Test avec un nouveau client temporaire
            from ..core.openai_client import OpenAIClient
            test_client = OpenAIClient(
                api_key=api_key or "sk-dummy",
                base_url=base_url,
                model=model,
                timeout=10
            )

            # Test simple
            response = test_client.simple_completion(
                prompt="Dis simplement 'connexion réussie'",
                system_prompt="Réponds brièvement.",
                max_tokens=50
            )

            if response:
                self.status_label.config(
                    text="✅ Connexion réussie ! Vous pouvez enregistrer.",
                    bootstyle=SUCCESS
                )
                self.save_btn.config(state="normal")
                messagebox.showinfo(
                    "Succès",
                    "La connexion à l'IA fonctionne correctement !\n\nVous pouvez maintenant enregistrer la configuration."
                )
            else:
                raise Exception("Aucune réponse de l'API")

        except Exception as e:
            logger.error(f"Erreur lors du test de connexion: {e}")
            self.status_label.config(
                text=f"❌ Erreur de connexion: {str(e)}",
                bootstyle=DANGER
            )
            messagebox.showerror(
                "Erreur de connexion",
                f"Impossible de se connecter à l'API:\n\n{str(e)}\n\nVérifiez vos paramètres et que le serveur IA est démarré."
            )
        finally:
            self.test_btn.config(state="normal", text="🔍 Tester la connexion")

    def _save_and_continue(self) -> None:
        """Enregistre la configuration et ferme l'assistant."""
        base_url = self.base_url_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        model = self.model_entry.get().strip()

        if not base_url or not model:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            # Mettre à jour la configuration
            config = self.config_manager.get_config()
            config.ai.base_url = base_url
            config.ai.api_key = api_key or "sk-dummy"
            config.ai.model = model
            config.first_run = False  # Marquer comme configuré

            # Sauvegarder
            self.config_manager.save_config()

            # Réinitialiser le client OpenAI avec les nouveaux paramètres
            from ..core.openai_client import init_openai_client
            init_openai_client(
                api_key=config.ai.api_key,
                base_url=config.ai.base_url,
                model=config.ai.model,
                temperature=config.ai.temperature,
                max_tokens=config.ai.max_tokens,
                timeout=config.ai.timeout,
                verify_ssl=config.ai.verify_ssl
            )

            logger.info("Configuration initiale sauvegardée")
            messagebox.showinfo(
                "Configuration enregistrée",
                "Votre configuration a été sauvegardée avec succès!\n\nL'application est prête à être utilisée."
            )

            self._close()

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            messagebox.showerror(
                "Erreur",
                f"Impossible de sauvegarder la configuration:\n\n{str(e)}"
            )

    def _skip(self) -> None:
        """Ignore la configuration initiale."""
        result = messagebox.askyesno(
            "Ignorer la configuration",
            "Êtes-vous sûr de vouloir ignorer la configuration ?\n\n"
            "Vous devrez configurer l'IA manuellement via le menu Paramètres avant de pouvoir utiliser les outils.",
            icon="warning"
        )

        if result:
            # Marquer comme non premier lancement
            config = self.config_manager.get_config()
            config.first_run = False
            self.config_manager.save_config()

            logger.info("Configuration initiale ignorée")
            self._close()

    def _close(self) -> None:
        """Ferme l'assistant."""
        if self.on_complete:
            self.on_complete()
        self.window.destroy()

