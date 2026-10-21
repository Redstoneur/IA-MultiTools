"""
Onglet de définition de mots et concepts.
"""

import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
from typing import Any

from ...core.config_manager import ConfigManager
from ..widgets.scrollable_form import ScrollableForm
from ...services.definition_service import get_definition_service

logger = logging.getLogger(__name__)


class DefinitionTab:
    """Onglet pour l'outil de définition."""

    def __init__(self, parent: Any, config_manager: ConfigManager) -> None:
        """
        Initialise l'onglet de définition.

        Args:
            parent: Widget parent
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.service = get_definition_service()

        # Frame principal
        self.frame = ScrollableForm(parent, padding=15)

        self._build_ui()
        logger.debug("Onglet Définition créé")

    def _build_ui(self) -> None:
        """Construit l'interface de l'onglet."""
        # Section entrée
        input_frame = ttk.Labelframe(self.frame, text="Entrée", padding=10)
        input_frame.pack(fill=X, pady=(0, 10))

        # Terme
        ttk.Label(input_frame, text="Mot ou concept:").pack(anchor=W, pady=(0, 5))
        self.term_entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.term_entry.pack(fill=X, pady=(0, 10))

        ttk.Label(input_frame, text="Instructions complémentaires (optionnel):").pack(anchor=W)
        self.instructions_entry = ttk.Entry(input_frame)
        self.instructions_entry.pack(fill=X, pady=(5, 10))

        # Limite de mots
        limit_frame = ttk.Frame(input_frame)
        limit_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(limit_frame, text="Limite de mots (optionnel):").pack(side=LEFT, padx=(0, 10))
        self.word_limit_var = tk.StringVar(value="")
        self.word_limit_spinbox = ttk.Spinbox(
            limit_frame,
            from_=10,
            to=500,
            textvariable=self.word_limit_var,
            width=10
        )
        self.word_limit_spinbox.pack(side=LEFT)

        # Format de sortie
        format_frame = ttk.Frame(input_frame)
        format_frame.pack(fill=X)

        ttk.Label(format_frame, text="Format:").pack(side=LEFT, padx=(0, 10))
        self.format_var = tk.StringVar(value="text")
        ttk.Radiobutton(
            format_frame,
            text="Texte",
            variable=self.format_var,
            value="text"
        ).pack(side=LEFT, padx=5)
        ttk.Radiobutton(
            format_frame,
            text="Markdown",
            variable=self.format_var,
            value="markdown"
        ).pack(side=LEFT, padx=5)

        # Boutons d'action
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=X, pady=10)

        self.generate_btn = ttk.Button(
            action_frame,
            text="🔍 Générer la définition",
            command=self._generate_definition,
            bootstyle=SUCCESS,
            width=25
        )
        self.generate_btn.pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            action_frame,
            text="📋 Copier",
            command=self._copy_result,
            bootstyle=INFO,
            width=15
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="🔄 Réinitialiser",
            command=self._reset,
            bootstyle=SECONDARY,
            width=15
        ).pack(side=LEFT, padx=5)

        # Section résultat
        result_frame = ttk.Labelframe(self.frame, text="Résultat", padding=10)
        result_frame.pack(fill=BOTH, expand=YES)

        # Zone de texte avec scrollbar
        text_container = ttk.Frame(result_frame)
        text_container.pack(fill=BOTH, expand=YES)

        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.result_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            yscrollcommand=scrollbar.set,
            relief=FLAT,
            bg="#2b2b2b" if self.config_manager.get_config().appearance.theme == "darkly" else "white",
            fg="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black",
            insertbackground="white" if self.config_manager.get_config().appearance.theme == "darkly" else "black"
        )
        self.result_text.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.config(command=self.result_text.yview)

    def _generate_definition(self) -> None:
        """Génère la définition."""
        term = self.term_entry.get().strip()

        if not term:
            messagebox.showwarning("Attention", "Veuillez entrer un mot ou concept.")
            return

        # Valider le terme
        valid, error_msg = self.service.validate_term(term)
        if not valid:
            messagebox.showerror("Erreur", error_msg)
            return

        # Obtenir la limite de mots
        word_limit = None
        if self.word_limit_var.get():
            try:
                word_limit = int(self.word_limit_var.get())
            except ValueError:
                pass

        # Obtenir le format de sortie
        output_format = self.format_var.get()
        instructions = self.instructions_entry.get().strip() or None
        self.service.set_system_prompt(self.config_manager.get_config().prompts.definition)

        # Désactiver le bouton pendant le traitement
        self.generate_btn.config(state="disabled", text="⏳ Génération en cours...")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "Génération de la définition en cours...\n\nVeuillez patienter.")

        # Lancer dans un thread séparé
        def process():
            try:
                result = self.service.get_definition(
                    term, word_limit=word_limit, output_format=output_format,
                    instructions=instructions,
                )

                # Mettre à jour l'UI dans le thread principal
                self.frame.after(0, lambda: self._update_result(result))
            except Exception as e:
                logger.error(f"Erreur lors de la génération: {e}")
                self.frame.after(0, lambda error=str(e): self._update_result(None, error))

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def _update_result(self, result: str | None, error: str | None = None) -> None:
        """
        Met à jour le résultat dans l'interface.

        Args:
            result: Résultat à afficher
            error: Message d'erreur optionnel
        """
        self.generate_btn.config(state="normal", text="🔍 Générer la définition")
        self.result_text.delete("1.0", tk.END)

        if error:
            self.result_text.insert("1.0", f"❌ Erreur:\n\n{error}")
            messagebox.showerror("Erreur", f"Impossible de générer la définition:\n\n{error}")
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
            messagebox.showinfo("Succès", "Résultat copié dans le presse-papiers!")
        else:
            messagebox.showwarning("Attention", "Aucun résultat à copier.")

    def _reset(self) -> None:
        """Réinitialise l'onglet."""
        self.term_entry.delete(0, tk.END)
        self.instructions_entry.delete(0, tk.END)
        self.word_limit_var.set("")
        self.result_text.delete("1.0", tk.END)
        self.format_var.set("text")
