"""
Fenêtre de paramètres de l'application.

Permet de configurer l'IA, la sécurité, l'apparence, et les prompts système.
"""

import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Optional

from ..core.config_manager import ConfigManager
from ..core.openai_client import get_openai_client
from ..core.authentication import get_auth_manager

logger = logging.getLogger(__name__)


class SettingsWindow:
    """
    Fenêtre de paramètres de l'application.

    Gère toutes les options configurables.
    """

    def __init__(self, parent: tk.Widget, config_manager: ConfigManager) -> None:
        """
        Initialise la fenêtre de paramètres.

        Args:
            parent: Widget parent
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()

        # Créer la fenêtre
        self.window = ttk.Toplevel(parent)
        self.window.title("Paramètres - IA-MultiTools")
        self.window.geometry("700x600")
        self.window.minsize(600, 500)

        # Rendre modale
        self.window.transient(parent)
        self.window.grab_set()

        self._build_ui()
        logger.info("Fenêtre de paramètres ouverte")

    def _build_ui(self) -> None:
        """Construit l'interface de la fenêtre."""
        # Frame principal avec scrollbar
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Créer le notebook pour les sections
        notebook = ttk.Notebook(main_container, bootstyle=INFO)
        notebook.pack(fill=BOTH, expand=YES, pady=(0, 10))

        # Onglets
        self._build_ai_config_tab(notebook)
        self._build_security_tab(notebook)
        self._build_appearance_tab(notebook)
        self._build_prompts_tab(notebook)

        # Boutons de contrôle
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=X)

        ttk.Button(
            control_frame,
            text="💾 Sauvegarder",
            command=self._save_settings,
            bootstyle=SUCCESS,
            width=20
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="🔄 Réinitialiser",
            command=self._reset_to_defaults,
            bootstyle=WARNING,
            width=20
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="❌ Annuler",
            command=self.window.destroy,
            bootstyle=SECONDARY,
            width=20
        ).pack(side=RIGHT, padx=5)

    def _build_ai_config_tab(self, notebook: ttk.Notebook) -> None:
        """Construit l'onglet de configuration IA."""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🤖 Configuration IA")

        # URL de base
        ttk.Label(frame, text="URL de base de l'API:").grid(row=0, column=0, sticky=W, pady=5)
        self.base_url_var = tk.StringVar(value=self.config.ai.base_url)
        ttk.Entry(frame, textvariable=self.base_url_var, width=50).grid(row=0, column=1, pady=5, padx=10)

        # Clé API
        ttk.Label(frame, text="Clé API:").grid(row=1, column=0, sticky=W, pady=5)
        self.api_key_var = tk.StringVar(value=self.config.ai.api_key)
        ttk.Entry(frame, textvariable=self.api_key_var, width=50, show="*").grid(row=1, column=1, pady=5, padx=10)

        # Modèle
        ttk.Label(frame, text="Modèle:").grid(row=2, column=0, sticky=W, pady=5)
        self.model_var = tk.StringVar(value=self.config.ai.model)
        ttk.Entry(frame, textvariable=self.model_var, width=50).grid(row=2, column=1, pady=5, padx=10)

        # Température
        ttk.Label(frame, text="Température (0.0 - 2.0):").grid(row=3, column=0, sticky=W, pady=5)
        self.temperature_var = tk.DoubleVar(value=self.config.ai.temperature)
        ttk.Spinbox(
            frame,
            from_=0.0,
            to=2.0,
            increment=0.1,
            textvariable=self.temperature_var,
            width=20
        ).grid(row=3, column=1, pady=5, padx=10, sticky=W)

        # Timeout
        ttk.Label(frame, text="Timeout (secondes):").grid(row=4, column=0, sticky=W, pady=5)
        self.timeout_var = tk.IntVar(value=self.config.ai.timeout)
        ttk.Spinbox(
            frame,
            from_=10,
            to=300,
            increment=10,
            textvariable=self.timeout_var,
            width=20
        ).grid(row=4, column=1, pady=5, padx=10, sticky=W)

        # Vérifier SSL
        self.verify_ssl_var = tk.BooleanVar(value=self.config.ai.verify_ssl)
        ttk.Checkbutton(
            frame,
            text="Vérifier les certificats SSL",
            variable=self.verify_ssl_var
        ).grid(row=5, column=1, pady=10, sticky=W, padx=10)

        # Bouton de test
        ttk.Button(
            frame,
            text="🔍 Tester la connexion",
            command=self._test_connection,
            bootstyle=INFO
        ).grid(row=6, column=1, pady=10, sticky=W, padx=10)

    def _build_security_tab(self, notebook: ttk.Notebook) -> None:
        """Construit l'onglet de sécurité."""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🔐 Sécurité")

        # Chiffrement
        self.encryption_var = tk.BooleanVar(value=self.config.security.encryption_enabled)
        ttk.Checkbutton(
            frame,
            text="Activer le chiffrement des données",
            variable=self.encryption_var
        ).pack(anchor=W, pady=10)

        # Trousseau système
        self.keyring_var = tk.BooleanVar(value=self.config.security.use_keyring)
        ttk.Checkbutton(
            frame,
            text="Utiliser le trousseau système (recommandé)",
            variable=self.keyring_var
        ).pack(anchor=W, pady=10)

        # Verrouillage de l'application
        self.app_lock_var = tk.BooleanVar(value=self.config.security.app_lock_enabled)
        ttk.Checkbutton(
            frame,
            text="Activer le verrouillage de l'application",
            variable=self.app_lock_var
        ).pack(anchor=W, pady=10)

        # Auto-verrouillage
        lock_frame = ttk.Labelframe(frame, text="Verrouillage automatique", padding=10)
        lock_frame.pack(fill=X, pady=10)

        ttk.Label(lock_frame, text="Délai d'inactivité (minutes):").pack(anchor=W, pady=5)

        self.auto_lock_var = tk.IntVar(value=self.config.security.auto_lock_minutes)
        options_frame = ttk.Frame(lock_frame)
        options_frame.pack(fill=X, pady=5)

        for value, label in [(0, "Désactivé"), (5, "5 min"), (15, "15 min"), (30, "30 min"), (60, "60 min")]:
            ttk.Radiobutton(
                options_frame,
                text=label,
                variable=self.auto_lock_var,
                value=value
            ).pack(side=LEFT, padx=10)

    def _build_appearance_tab(self, notebook: ttk.Notebook) -> None:
        """Construit l'onglet d'apparence."""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="🎨 Apparence")

        # Thème
        ttk.Label(frame, text="Thème:").pack(anchor=W, pady=5)

        self.theme_var = tk.StringVar(value=self.config.appearance.theme)
        theme_frame = ttk.Frame(frame)
        theme_frame.pack(fill=X, pady=10)

        themes = ["darkly", "solar", "superhero", "cyborg", "vapor", "cosmo", "flatly", "journal", "litera"]

        for i, theme in enumerate(themes):
            ttk.Radiobutton(
                theme_frame,
                text=theme.capitalize(),
                variable=self.theme_var,
                value=theme
            ).grid(row=i//3, column=i%3, sticky=W, padx=10, pady=5)

        # Taille de police
        font_frame = ttk.Frame(frame)
        font_frame.pack(fill=X, pady=10)

        ttk.Label(font_frame, text="Taille de police:").pack(side=LEFT, padx=10)

        self.font_size_var = tk.IntVar(value=self.config.appearance.font_size)
        ttk.Spinbox(
            font_frame,
            from_=8,
            to=18,
            textvariable=self.font_size_var,
            width=10
        ).pack(side=LEFT)

        # Note
        ttk.Label(
            frame,
            text="⚠ Le changement de thème nécessite un redémarrage de l'application.",
            foreground="orange"
        ).pack(anchor=W, pady=20)

    def _build_prompts_tab(self, notebook: ttk.Notebook) -> None:
        """Construit l'onglet des prompts système."""
        frame = ttk.Frame(notebook, padding=15)
        notebook.add(frame, text="📝 Prompts système")

        # Scrollable frame
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Prompt Définition
        ttk.Label(scrollable_frame, text="Prompt Définition:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(5, 5))
        self.prompt_definition_text = tk.Text(scrollable_frame, height=4, wrap=tk.WORD)
        self.prompt_definition_text.insert("1.0", self.config.prompts.definition)
        self.prompt_definition_text.pack(fill=X, pady=(0, 15))

        # Prompt Synonymes
        ttk.Label(scrollable_frame, text="Prompt Synonymes:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(5, 5))
        self.prompt_synonym_text = tk.Text(scrollable_frame, height=4, wrap=tk.WORD)
        self.prompt_synonym_text.insert("1.0", self.config.prompts.synonym)
        self.prompt_synonym_text.pack(fill=X, pady=(0, 15))

        # Prompt Correction de texte
        ttk.Label(scrollable_frame, text="Prompt Correction de texte:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(5, 5))
        self.prompt_text_correction_text = tk.Text(scrollable_frame, height=4, wrap=tk.WORD)
        self.prompt_text_correction_text.insert("1.0", self.config.prompts.text_correction)
        self.prompt_text_correction_text.pack(fill=X, pady=(0, 15))

        # Prompt E-mails
        ttk.Label(scrollable_frame, text="Prompt E-mails:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(5, 5))
        self.prompt_email_text = tk.Text(scrollable_frame, height=4, wrap=tk.WORD)
        self.prompt_email_text.insert("1.0", self.config.prompts.email_correction)
        self.prompt_email_text.pack(fill=X, pady=(0, 15))

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _test_connection(self) -> None:
        """Teste la connexion à l'API."""
        # Mettre à jour temporairement le client avec les nouvelles valeurs
        try:
            client = get_openai_client()
            client.update_config(
                api_key=self.api_key_var.get(),
                base_url=self.base_url_var.get(),
                model=self.model_var.get(),
                temperature=self.temperature_var.get(),
                timeout=self.timeout_var.get(),
                verify_ssl=self.verify_ssl_var.get()
            )

            success, message = client.test_connection()

            if success:
                messagebox.showinfo("Test de connexion", "✓ Connexion réussie!")
            else:
                messagebox.showerror("Test de connexion", f"✗ Échec de la connexion:\n\n{message}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test:\n\n{str(e)}")

    def _save_settings(self) -> None:
        """Sauvegarde les paramètres."""
        try:
            # Mettre à jour la configuration
            self.config.ai.api_key = self.api_key_var.get()
            self.config.ai.base_url = self.base_url_var.get()
            self.config.ai.model = self.model_var.get()
            self.config.ai.temperature = self.temperature_var.get()
            self.config.ai.timeout = self.timeout_var.get()
            self.config.ai.verify_ssl = self.verify_ssl_var.get()

            self.config.security.encryption_enabled = self.encryption_var.get()
            self.config.security.use_keyring = self.keyring_var.get()
            self.config.security.app_lock_enabled = self.app_lock_var.get()
            self.config.security.auto_lock_minutes = self.auto_lock_var.get()

            self.config.appearance.theme = self.theme_var.get()
            self.config.appearance.font_size = self.font_size_var.get()

            self.config.prompts.definition = self.prompt_definition_text.get("1.0", tk.END).strip()
            self.config.prompts.synonym = self.prompt_synonym_text.get("1.0", tk.END).strip()
            self.config.prompts.text_correction = self.prompt_text_correction_text.get("1.0", tk.END).strip()
            self.config.prompts.email_correction = self.prompt_email_text.get("1.0", tk.END).strip()

            # Valider la configuration
            valid, errors = self.config_manager.validate()
            if not valid:
                messagebox.showerror("Erreur de validation", "\n".join(errors))
                return

            # Sauvegarder
            self.config_manager.save_config()

            messagebox.showinfo("Succès", "Les paramètres ont été sauvegardés avec succès!")
            logger.info("Paramètres sauvegardés")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite:\n\n{str(e)}")

    def _reset_to_defaults(self) -> None:
        """Réinitialise aux valeurs par défaut."""
        response = messagebox.askyesno(
            "Confirmer",
            "Voulez-vous vraiment réinitialiser tous les paramètres aux valeurs par défaut?"
        )

        if response:
            self.config_manager.reset_to_defaults()
            self.config = self.config_manager.get_config()
            self.window.destroy()
            messagebox.showinfo("Succès", "Paramètres réinitialisés. Veuillez redémarrer l'application.")

    def _on_app_lock_changed(self) -> None:
        """Appelé quand l'option app_lock change."""
        self._set_password()

    def _set_password(self) -> None:
        """Ouvre le dialogue pour définir/changer le mot de passe."""
        dialog = ttk.Toplevel(self.window)
        dialog.title("Définir un mot de passe")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        # Centre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f'400x300+{x}+{y}')

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        ttk.Label(frame, text="Définir un mot de passe", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        # Nouveau mot de passe
        ttk.Label(frame, text="Nouveau mot de passe:").pack(anchor=W, pady=(0, 5))
        password_entry = ttk.Entry(frame, show="●", font=("Segoe UI", 10))
        password_entry.pack(fill=X, pady=(0, 10))

        # Confirmation
        ttk.Label(frame, text="Confirmer le mot de passe:").pack(anchor=W, pady=(0, 5))
        confirm_entry = ttk.Entry(frame, show="●", font=("Segoe UI", 10))
        confirm_entry.pack(fill=X, pady=(0, 10))

        status_label = ttk.Label(frame, text="", foreground="red")
        status_label.pack(pady=10)

        def save_password():
            password = password_entry.get()
            confirm = confirm_entry.get()

            if not password:
                status_label.config(text="⚠ Le mot de passe ne peut pas être vide")
                return

            if len(password) < 4:
                status_label.config(text="⚠ Le mot de passe doit contenir au moins 4 caractères")
                return

            if password != confirm:
                status_label.config(text="❌ Les mots de passe ne correspondent pas")
                return

            if self.config_manager.set_password(password):
                messagebox.showinfo("Succès", "Mot de passe défini avec succès!", parent=dialog)
                self._update_password_status()
                dialog.destroy()
            else:
                status_label.config(text="❌ Erreur lors de la définition du mot de passe")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="✓ Enregistrer", command=save_password, bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=5)

    def _remove_password(self) -> None:
        """Supprime le mot de passe."""
        result = messagebox.askyesno(
            "Supprimer le mot de passe",
            "Êtes-vous sûr de vouloir supprimer le mot de passe ?\n\n"
            "Le verrouillage de l'application sera désactivé.",
            icon="warning",
            parent=self.window
        )

        if result:
            if self.config_manager.remove_password():
                self.app_lock_var.set(False)
                self.config.security.app_lock_enabled = False
                self.config_manager.save_config()
                messagebox.showinfo("Succès", "Mot de passe supprimé", parent=self.window)
                self._update_password_status()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer le mot de passe", parent=self.window)

    def _update_password_status(self) -> None:
        """Met à jour le statut du mot de passe."""
        status_text = "✅ Un mot de passe est défini" if self.config_manager.has_password() else "⚠ Aucun mot de passe défini"
        self.password_status_label.config(text=status_text)
