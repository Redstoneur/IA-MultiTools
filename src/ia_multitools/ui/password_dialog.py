"""
Boîte de dialogue d'authentification par mot de passe.
"""

import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from typing import Any, Optional, Callable

from ..core.authentication import AuthenticationManager

logger = logging.getLogger(__name__)


class PasswordDialog:
    """Boîte de dialogue d'authentification par mot de passe."""

    def __init__(
        self,
        parent: Any,
        auth_manager: AuthenticationManager,
        on_success: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        is_startup: bool = True
    ) -> None:
        """
        Initialise la boîte de dialogue de mot de passe.

        Args:
            parent: Widget parent
            auth_manager: Gestionnaire d'authentification
            on_success: Callback appelé en cas de succès
            on_cancel: Callback appelé en cas d'annulation
            is_startup: True si c'est au démarrage (pas de bouton annuler)
        """
        self.auth_manager = auth_manager
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.is_startup = is_startup
        self.authenticated = False

        # Fenêtre modale
        self.window = ttk.Toplevel(parent) if parent else ttk.Window(themename="darkly")
        self.window.title("🔒 Authentification - IA-MultiTools")
        self.window.geometry("450x300")
        self.window.resizable(False, False)

        if parent:
            self.window.transient(parent)
            self.window.grab_set()

        # Empêcher la fermeture via X si c'est au démarrage
        if is_startup:
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel_startup)
        else:
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Centrer la fenêtre
        self._center_window()

        self._build_ui()

        # Focus sur le champ de mot de passe
        self.password_entry.focus()

        logger.info("Boîte de dialogue d'authentification ouverte")

    def _center_window(self) -> None:
        """Centre la fenêtre sur l'écran."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _build_ui(self) -> None:
        """Construit l'interface de la boîte de dialogue."""
        # Conteneur principal
        main_frame = ttk.Frame(self.window, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            header_frame,
            text="🔒 Application Verrouillée",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=CENTER)

        if self.is_startup:
            message = "Entrez votre mot de passe pour démarrer l'application"
        else:
            message = "Entrez votre mot de passe pour déverrouiller"

        ttk.Label(
            header_frame,
            text=message,
            font=("Segoe UI", 10)
        ).pack(anchor=CENTER, pady=(10, 0))

        # Séparateur
        ttk.Separator(main_frame).pack(fill=X, pady=15)

        # Champ de mot de passe
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=X, pady=10)

        ttk.Label(
            password_frame,
            text="Mot de passe:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))

        self.password_entry = ttk.Entry(
            password_frame,
            font=("Segoe UI", 11),
            show="●",
            width=30
        )
        self.password_entry.pack(fill=X)
        self.password_entry.bind("<Return>", lambda e: self._verify())

        # Label de statut
        self.status_label = ttk.Label(
            password_frame,
            text="",
            font=("Segoe UI", 9),
            foreground="red"
        )
        self.status_label.pack(anchor=W, pady=(5, 0))

        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(20, 0))

        self.verify_btn = ttk.Button(
            button_frame,
            text="✓ Déverrouiller",
            command=self._verify,
            bootstyle=SUCCESS,
            width=20
        )
        self.verify_btn.pack(side=LEFT, padx=(0, 10))

        if not self.is_startup:
            ttk.Button(
                button_frame,
                text="Annuler",
                command=self._on_cancel,
                bootstyle=SECONDARY,
                width=15
            ).pack(side=LEFT)
        else:
            ttk.Button(
                button_frame,
                text="🚪 Quitter",
                command=self._on_cancel_startup,
                bootstyle=DANGER,
                width=15
            ).pack(side=RIGHT)

    def _verify(self) -> None:
        """Vérifie le mot de passe."""
        password = self.password_entry.get()

        if not password:
            self.status_label.config(text="⚠ Veuillez entrer un mot de passe")
            return

        # Désactiver le bouton pendant la vérification
        self.verify_btn.config(state="disabled", text="⏳ Vérification...")
        self.window.update()

        try:
            if self.auth_manager.verify_password(password):
                logger.info("Authentification réussie")
                self.authenticated = True

                if self.on_success:
                    self.on_success()

                self.window.destroy()
            else:
                logger.warning("Mot de passe incorrect")
                self.status_label.config(text="❌ Mot de passe incorrect")
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()

        except Exception as e:
            logger.error(f"Erreur lors de la vérification: {e}")
            self.status_label.config(text=f"❌ Erreur: {str(e)}")

        finally:
            self.verify_btn.config(state="normal", text="✓ Déverrouiller")

    def _on_cancel(self) -> None:
        """Gère l'annulation."""
        logger.info("Authentification annulée")

        if self.on_cancel:
            self.on_cancel()

        self.window.destroy()

    def _on_cancel_startup(self) -> None:
        """Gère l'annulation au démarrage (quitte l'application)."""
        result = messagebox.askyesno(
            "Quitter",
            "Voulez-vous vraiment quitter l'application ?",
            icon="warning",
            parent=self.window
        )

        if result:
            logger.info("Quitter l'application depuis l'authentification")
            self.window.destroy()
            # Quitter complètement
            import sys
            sys.exit(0)

    def wait(self) -> bool:
        """
        Attends la fermeture de la fenêtre et retourne le résultat.

        Returns:
            True si authentifié, False sinon
        """
        self.window.wait_window()
        return self.authenticated


