"""
Assistant de configuration initiale au premier lancement.
"""

import logging
import copy
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import messagebox
from typing import Any, Optional, Callable

from ..core.config_manager import ConfigManager
from ..core.openai_client import OpenAIClient
from .widgets.ai_settings import validate_ai_settings

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
        self._last_successful_test_signature: Optional[
            tuple[str, str, str, float, int, bool]
        ] = None

        # Fenêtre modale
        self.window = ttk.Toplevel(parent)
        self.window.title("🚀 Configuration initiale - IA-MultiTools")
        width = min(900, self.window.winfo_screenwidth() - 80)
        height = min(760, self.window.winfo_screenheight() - 100)
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(min(500, width), min(400, height))
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()

        self._build_ui()
        self._center_window()

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
        config = self.config_manager.get_config().ai
        self.base_url_var = tk.StringVar(value=config.base_url)
        self.api_key_var = tk.StringVar(value=config.api_key)
        self.model_var = tk.StringVar(value=config.model)
        self.temperature_var = tk.StringVar(value=str(config.temperature))
        self.timeout_var = tk.StringVar(value=str(config.timeout))
        self.verify_ssl_var = tk.BooleanVar(value=config.verify_ssl)

        # Conteneur principal
        outer_frame = ttk.Frame(self.window, padding=20)
        outer_frame.pack(fill=BOTH, expand=YES)
        button_frame = ttk.Frame(outer_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=(15, 0))
        button_frame.columnconfigure((0, 1), weight=1, uniform="actions")

        self.form = ScrolledFrame(outer_frame, autohide=False)
        self.form.pack(fill=BOTH, expand=YES)
        main_frame = ttk.Frame(self.form, padding=(0, 0, 15, 0))
        main_frame.pack(fill=BOTH, expand=YES)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            header_frame,
            text="🎉 Bienvenue dans IA-MultiTools !",
            font=("Segoe UI", 18, "bold"),
            wraplength=420
        ).pack(anchor=W)

        ttk.Label(
            header_frame,
            text="Configurons votre connexion IA pour commencer",
            font=("Segoe UI", 11),
            wraplength=420
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
            foreground="gray",
            wraplength=420
        ).pack(anchor=W, pady=(0, 5))

        self.base_url_entry = ttk.Entry(
            config_frame, font=("Segoe UI", 10), textvariable=self.base_url_var
        )
        self.base_url_entry.pack(fill=X, pady=(0, 15))

        # Clé API
        ttk.Label(config_frame, text="Clé API (optionnel pour serveurs locaux):", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        self.api_key_entry = ttk.Entry(
            config_frame, font=("Segoe UI", 10), show="*", textvariable=self.api_key_var
        )
        self.api_key_entry.pack(fill=X, pady=(0, 15))

        self.verify_ssl_check = ttk.Checkbutton(
            config_frame,
            text="Vérifier les certificats SSL",
            variable=self.verify_ssl_var,
        )
        self.verify_ssl_check.pack(anchor=W, pady=(0, 5))
        ttk.Label(
            config_frame,
            text="Recommandé : laissez cette option activée. La désactiver rend les connexions HTTPS non vérifiées.",
            bootstyle=WARNING,
            wraplength=420,
        ).pack(anchor=W, pady=(0, 15))

        # Modèle
        ttk.Label(config_frame, text="Nom du modèle:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(0, 5))
        self.model_entry = ttk.Combobox(
            config_frame, font=("Segoe UI", 10), textvariable=self.model_var, state="normal"
        )
        self.model_entry.pack(fill=X, pady=(0, 5))
        self.models_btn = ttk.Button(
            config_frame, text="Charger les modèles disponibles",
            command=self._load_models, bootstyle=INFO,
        )
        self.models_btn.pack(anchor=W, pady=(0, 5))
        ttk.Label(
            config_frame,
            text="Liste fournie par votre serveur API. Vous pouvez aussi saisir un nom manuellement.",
            wraplength=420,
        ).pack(anchor=W, pady=(0, 15))

        ttk.Label(
            config_frame, text="Température (0.0 - 2.0):", font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))
        self.temperature_entry = ttk.Spinbox(
            config_frame, from_=0.0, to=2.0, increment=0.1,
            textvariable=self.temperature_var,
        )
        self.temperature_entry.pack(fill=X, pady=(0, 15))
        ttk.Label(
            config_frame, text="Timeout (secondes):", font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))
        self.timeout_entry = ttk.Spinbox(
            config_frame, from_=1, to=300, increment=10,
            textvariable=self.timeout_var,
        )
        self.timeout_entry.pack(fill=X, pady=(0, 15))
        for entry in (
            self.base_url_entry, self.api_key_entry, self.model_entry,
            self.temperature_entry, self.timeout_entry, self.verify_ssl_check,
            self.models_btn,
        ):
            entry.bind("<FocusIn>", self._scroll_to_field)

        # Zone de statut
        self.status_label = ttk.Label(
            config_frame,
            text="",
            font=("Segoe UI", 9),
            bootstyle=INFO,
            wraplength=420
        )
        self.status_label.pack(fill=X, pady=10)

        # Boutons d'action
        self.test_btn = ttk.Button(
            button_frame,
            text="🔍 Tester la connexion",
            command=self._test_connection,
            bootstyle=INFO
        )
        self.test_btn.grid(row=0, column=0, sticky=EW, padx=(0, 5))

        self.save_btn = ttk.Button(
            button_frame,
            text="✓ Enregistrer et continuer",
            command=self._save_and_continue,
            bootstyle=SUCCESS,
            state="disabled"
        )
        self.save_btn.grid(row=0, column=1, sticky=EW, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Ignorer (configurer plus tard)",
            command=self._skip,
            bootstyle=SECONDARY
        ).grid(row=1, column=0, columnspan=2, sticky=EW, pady=(10, 0))

        # Instructions
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=X, pady=(15, 0))

        ttk.Label(
            info_frame,
            text="💡 Astuce: Vous pouvez toujours modifier ces paramètres via le menu Paramètres.",
            font=("Segoe UI", 9),
            foreground="gray",
            wraplength=420
        ).pack()
        for frame in (header_frame, config_frame, info_frame):
            frame.bind("<Configure>", self._wrap_labels)
        for variable in (
            self.base_url_var, self.api_key_var, self.model_var,
            self.temperature_var, self.timeout_var, self.verify_ssl_var,
        ):
            variable.trace_add("write", self._invalidate_test)
        for variable in (self.base_url_var, self.api_key_var, self.verify_ssl_var):
            variable.trace_add("write", self._clear_models)

    def _invalidate_test(self, *_args: str) -> None:
        self._last_successful_test_signature = None
        self.save_btn.config(state="disabled")
        self.status_label.config(text="Paramètres modifiés : testez la connexion.", bootstyle=INFO)

    def _clear_models(self, *_args: str) -> None:
        self.model_entry.configure(values=())

    def _get_ai_signature(self, require_model: bool = True) -> tuple[str, str, str, float, int, bool]:
        return validate_ai_settings(
            self.base_url_var.get(), self.model_var.get(), self.api_key_var.get(),
            self.temperature_var.get(), self.timeout_var.get(), self.verify_ssl_var.get(),
            require_model=require_model,
        )

    def _load_models(self) -> None:
        """Récupère les modèles avec les paramètres de connexion actuels."""
        try:
            base_url, model, api_key, temperature, timeout, verify_ssl = self._get_ai_signature(False)
        except ValueError as exc:
            messagebox.showerror("Paramètres invalides", str(exc), parent=self.window)
            return

        self.models_btn.config(state="disabled")
        self.status_label.config(text="Chargement des modèles...", bootstyle=INFO)
        self.window.update_idletasks()
        client: Optional[OpenAIClient] = None
        try:
            client = OpenAIClient(
                api_key=api_key or "sk-dummy", base_url=base_url, model=model,
                temperature=temperature, timeout=timeout, verify_ssl=verify_ssl,
            )
            models = sorted(set(client.list_models()))
            self.model_entry.configure(values=models)
            if not models:
                self.status_label.config(text="Aucun modèle récupéré.", bootstyle=WARNING)
                messagebox.showwarning(
                    "Modèles indisponibles",
                    "Aucun modèle récupéré. Vérifiez l'URL, la clé API, le réglage SSL "
                    "et la disponibilité du serveur. La saisie manuelle reste possible.",
                    parent=self.window,
                )
                return
            if model not in models:
                self.model_var.set(models[0])
            self.status_label.config(
                text=f"{len(models)} modèle(s) disponible(s). Choisissez puis testez la connexion.",
                bootstyle=INFO,
            )
        except Exception as exc:
            logger.error("Erreur lors du chargement des modèles: %s", type(exc).__name__)
            self.model_entry.configure(values=())
            self.status_label.config(text="Chargement des modèles impossible.", bootstyle=DANGER)
            messagebox.showerror(
                "Erreur", f"Impossible de charger les modèles ({type(exc).__name__}).",
                parent=self.window,
            )
        finally:
            if client is not None:
                client.close()
            self.models_btn.config(state="normal")

    def _wrap_labels(self, event: tk.Event) -> None:
        """Adapte les textes à la largeur disponible dans le formulaire."""
        for widget in event.widget.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(wraplength=max(1, event.width - 40))

    def _scroll_to_field(self, event: tk.Event) -> None:
        """Garde le champ actif visible lors de la navigation au clavier."""
        field = event.widget
        top = self.form.container.winfo_rooty()
        bottom = top + self.form.container.winfo_height()
        if field.winfo_rooty() < top or field.winfo_rooty() + field.winfo_height() > bottom:
            offset = field.winfo_rooty() - self.form.winfo_rooty()
            self.form.yview_moveto(max(0, offset - 10) / self.form.winfo_height())

    def _test_connection(self) -> None:
        """Teste la connexion à l'API."""
        try:
            signature = self._get_ai_signature()
        except ValueError as exc:
            messagebox.showerror("Paramètres invalides", str(exc), parent=self.window)
            return
        base_url, model, api_key, temperature, timeout, verify_ssl = signature

        # Désactiver les boutons pendant le test
        self._last_successful_test_signature = None
        self.test_btn.config(state="disabled", text="⏳ Test en cours...")
        self.save_btn.config(state="disabled")
        self.status_label.config(text="Test de connexion en cours...", bootstyle=INFO)

        self.window.update()

        test_client: Optional[OpenAIClient] = None
        try:
            # Test avec un nouveau client temporaire
            test_client = OpenAIClient(
                api_key=api_key or "sk-dummy",
                base_url=base_url,
                model=model,
                temperature=temperature,
                timeout=timeout,
                verify_ssl=verify_ssl,
            )

            # Test simple
            response = test_client.simple_completion(
                prompt="Dis simplement 'connexion réussie'",
                system_prompt="Réponds brièvement.",
                max_tokens=50
            )

            if response:
                self._last_successful_test_signature = signature
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
            logger.error("Erreur lors du test de connexion: %s", type(e).__name__)
            error_message = f"Erreur de connexion ({type(e).__name__})"
            self.status_label.config(
                text=f"❌ {error_message}",
                bootstyle=DANGER
            )
            messagebox.showerror(
                "Erreur de connexion",
                f"Impossible de préparer la connexion ({type(e).__name__}). "
                "Vérifiez vos paramètres et que le serveur IA est démarré."
            )
        finally:
            if test_client is not None:
                test_client.close()
            self.test_btn.config(state="normal", text="🔍 Tester la connexion")

    def _save_and_continue(self) -> None:
        """Enregistre la configuration et ferme l'assistant."""
        try:
            signature = self._get_ai_signature()
        except ValueError as exc:
            messagebox.showerror("Paramètres invalides", str(exc), parent=self.window)
            return
        base_url, model, api_key, temperature, timeout, verify_ssl = signature

        if self._last_successful_test_signature != signature:
            self.save_btn.config(state="disabled")
            messagebox.showerror(
                "Test requis",
                "Testez avec succès la connexion avec les paramètres actuels avant de les enregistrer.",
            )
            return

        try:
            # Mettre à jour la configuration
            config = self.config_manager.get_config()
            previous_config = copy.deepcopy(config)
            config.ai.base_url = base_url
            config.ai.api_key = api_key
            config.ai.model = model
            config.ai.temperature = temperature
            config.ai.timeout = timeout
            config.ai.verify_ssl = verify_ssl
            config.first_run = False  # Marquer comme configuré

            # Sauvegarder
            if not self.config_manager.save_config():
                self.config_manager.config = previous_config
                raise RuntimeError(
                    "La configuration n'a pas pu être sauvegardée. "
                    "Vérifiez la disponibilité du trousseau système."
                )

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
            logger.error("Erreur lors de la sauvegarde: %s", type(e).__name__)
            messagebox.showerror(
                "Erreur",
                f"Impossible de sauvegarder la configuration ({type(e).__name__})."
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
            if not self.config_manager.save_config():
                messagebox.showerror(
                    "Erreur",
                    "Impossible de sauvegarder la configuration. Vérifiez le trousseau système.",
                    parent=self.window,
                )
                config.first_run = True
                return

            logger.info("Configuration initiale ignorée")
            self._close()

    def _close(self) -> None:
        """Ferme l'assistant."""
        if self.on_complete:
            self.on_complete()
        self.window.destroy()
