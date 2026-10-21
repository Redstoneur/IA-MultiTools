"""Panel for correcting and translating text."""

import tkinter as tk
import ttkbootstrap as ttk

from .correction_tab import CorrectionTab
from ...services.translation_service import TranslationService


class TranslationTab(CorrectionTab):
    """Share the correction editor, with an explicit target language."""

    ACTION_TEXT = "Corriger et traduire"
    RESULT_TITLE = "Texte corrigé et traduit"
    PROMPT_NAME = "translation"

    def _get_service(self):
        return TranslationService()

    def _build_extra_options(self, parent) -> None:
        ttk.Label(parent, text="Langue cible (langue source détectée automatiquement):").pack(
            anchor="w", pady=(10, 5)
        )
        self.target_language_var = tk.StringVar(value="Anglais")
        self.target_language_entry = ttk.Combobox(
            parent, textvariable=self.target_language_var,
            values=("Anglais", "Français", "Espagnol", "Allemand", "Italien",
                    "Portugais", "Néerlandais", "Arabe", "Chinois", "Japonais"),
            state="normal",
        )
        self.target_language_entry.pack(fill="x")

    def _request_options(self) -> dict:
        language = self.target_language_var.get().strip()
        if not language or len(language) > 100:
            raise ValueError("Renseignez une langue cible (100 caractères maximum).")
        return {"target_language": language}

    def _reset(self) -> None:
        super()._reset()
        self.target_language_var.set("Anglais")
