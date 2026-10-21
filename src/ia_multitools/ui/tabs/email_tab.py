"""
Onglet de correction d'e-mails.
"""

import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
from typing import Any

from ...core.config_manager import ConfigManager
from ...services.email_correction_service import get_email_correction_service

logger = logging.getLogger(__name__)


class EmailTab:
    """Onglet pour l'outil de correction d'e-mails."""

    def __init__(self, parent: Any, config_manager: ConfigManager) -> None:
        """
        Initialise l'onglet d'e-mails.

        Args:
            parent: Widget parent
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.service = get_email_correction_service()

        # Frame principal
        self.frame = ttk.Frame(parent, padding=15)

        self._build_ui()
        logger.debug("Onglet E-mails créé")

    def _build_ui(self) -> None:
        """Construit l'interface de l'onglet."""
        # Section entrée
        input_frame = ttk.Labelframe(self.frame, text="Contenu de l'e-mail", padding=10)
        input_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))

        # Zone de texte d'entrée avec scrollbar
        text_input_container = ttk.Frame(input_frame)
        text_input_container.pack(fill=BOTH, expand=YES, pady=(0, 10))

        scrollbar_input = ttk.Scrollbar(text_input_container)
        scrollbar_input.pack(side=RIGHT, fill=Y)

        self.input_text = tk.Text(
            text_input_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            yscrollcommand=scrollbar_input.set,
            relief=FLAT,
            height=7,
            bg="#2b2b2b" if self.config_manager.get_config().appearance.theme == "darkly" else "white",
            fg="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black",
            insertbackground="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black"
        )
        self.input_text.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar_input.config(command=self.input_text.yview)

        # Options
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill=X, pady=(5, 5))

        self.make_professional_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Rendre professionnel",
            variable=self.make_professional_var
        ).pack(side=LEFT, padx=(0, 15))

        self.add_greeting_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Ajouter formule de politesse",
            variable=self.add_greeting_var
        ).pack(side=LEFT, padx=(0, 15))

        # Instructions complémentaires
        ttk.Label(input_frame, text="Instructions complémentaires (optionnel):").pack(anchor=W, pady=(5, 5))
        self.instructions_entry = ttk.Entry(input_frame, font=("Segoe UI", 10))
        self.instructions_entry.pack(fill=X)

        # Boutons d'action
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=X, pady=10)

        self.correct_btn = ttk.Button(
            action_frame,
            text="✓ Corriger l'e-mail",
            command=self._correct_email,
            bootstyle=SUCCESS,
            width=25
        )
        self.correct_btn.pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            action_frame,
            text="📋 Copier le résultat",
            command=self._copy_result,
            bootstyle=INFO,
            width=18
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="🔄 Réinitialiser",
            command=self._reset,
            bootstyle=SECONDARY,
            width=15
        ).pack(side=LEFT, padx=5)

        # Section résultat
        result_frame = ttk.Labelframe(self.frame, text="E-mail corrigé", padding=10)
        result_frame.pack(fill=BOTH, expand=YES)

        # Zone de texte de résultat avec scrollbar
        text_result_container = ttk.Frame(result_frame)
        text_result_container.pack(fill=BOTH, expand=YES)

        scrollbar_result = ttk.Scrollbar(text_result_container)
        scrollbar_result.pack(side=RIGHT, fill=Y)

        self.result_text = tk.Text(
            text_result_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            yscrollcommand=scrollbar_result.set,
            relief=FLAT,
            bg="#2b2b2b" if self.config_manager.get_config().appearance.theme == "darkly" else "white",
            fg="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black",
            insertbackground="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black"
        )
        self.result_text.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar_result.config(command=self.result_text.yview)

    def _correct_email(self) -> None:
        """Corrige l'e-mail."""
        content = self.input_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showwarning("Attention", "Veuillez entrer le contenu de l'e-mail.")
            return

        # Valider le contenu
        valid, error_msg = self.service.validate_email(content)
        if not valid:
            messagebox.showerror("Erreur", error_msg)
            return

        instructions = self.instructions_entry.get().strip() or None
        make_professional = self.make_professional_var.get()
        add_greeting = self.add_greeting_var.get()

        # Désactiver le bouton pendant le traitement
        self.correct_btn.config(state="disabled", text="⏳ Correction en cours...")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "Correction de l'e-mail en cours...\n\nVeuillez patienter.")

        # Lancer dans un thread séparé
        def process():
            try:
                result = self.service.correct_email(
                    content=content,
                    instructions=instructions,
                    make_professional=make_professional,
                    add_greeting=add_greeting
                )

                # Mettre à jour l'UI dans le thread principal
                self.frame.after(0, lambda: self._update_result(result))
            except Exception as e:
                logger.error(f"Erreur lors de la correction: {e}")
                self.frame.after(0, lambda: self._update_result(None, str(e)))

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def _update_result(self, result: str | None, error: str | None = None) -> None:
        """
        Met à jour le résultat dans l'interface.

        Args:
            result: Résultat à afficher
            error: Message d'erreur optionnel
        """
        self.correct_btn.config(state="normal", text="✓ Corriger l'e-mail")
        self.result_text.delete("1.0", tk.END)

        if error:
            self.result_text.insert("1.0", f"❌ Erreur:\n\n{error}")
            messagebox.showerror("Erreur", f"Impossible de corriger l'e-mail:\n\n{error}")
        elif result:
            self.result_text.insert("1.0", result)
        else:
            self.result_text.insert("1.0", "❌ Aucun résultat obtenu.")
            messagebox.showwarning("Attention", "Aucun résultat n'a été obtenu de l'IA.")

    def _copy_result(self) -> None:
        """Copie le résultat dans le presse-papiers."""
        result = self.result_text.get("1.0", tk.END).strip()

        if result:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(result)
            messagebox.showinfo("Succès", "E-mail copié dans le presse-papiers!")
        else:
            messagebox.showwarning("Attention", "Aucun résultat à copier.")

    def _reset(self) -> None:
        """Réinitialise l'onglet."""
        self.input_text.delete("1.0", tk.END)
        self.instructions_entry.delete(0, tk.END)
        self.result_text.delete("1.0", tk.END)
        self.make_professional_var.set(False)
        self.add_greeting_var.set(True)
        self.format_var.set("text")
