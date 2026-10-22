"""Translation panel options and shared editor behavior."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import ttkbootstrap as ttk

from src.ia_multitools.ui.tabs.translation_tab import TranslationTab
from .test_first_run_wizard import config_manager, assert_inside


def test_translation_panel_passes_options_and_resets(root, monkeypatch):
    notebook = ttk.Notebook(root)
    manager = config_manager()
    service = Mock()
    service.validate_text.return_value = (True, "")
    service.correct_text.return_value = "Hello."
    with patch.object(TranslationTab, "_get_service", return_value=service):
        tab = TranslationTab(notebook, manager)
    monkeypatch.setattr(tab.frame, "after", lambda delay, callback: callback())
    monkeypatch.setattr(
        "src.ia_multitools.ui.tabs.correction_tab.threading.Thread",
        lambda target, **kwargs: Mock(start=target),
    )
    try:
        assert not tab.markdown_var.get()
        assert tab.target_language_var.get() == "Anglais"
        tab.input_text.insert("1.0", "bonjour")
        tab.instructions_entry.insert(0, "Ton amical.")
        tab.target_language_var.set("Espagnol")
        tab.markdown_var.set(True)
        tab._correct_text()
        service.correct_text.assert_called_once_with(
            "bonjour", instructions="Ton amical.", output_format="markdown",
            target_language="Espagnol",
        )
        service.set_system_prompt.assert_called_once_with(manager.get_config().prompts.translation)
        assert tab.result_text.get("1.0", "end").strip() == "Hello."
        assert tab.correct_btn["text"] == "Corriger et traduire"
        tab._reset()
        assert tab.target_language_var.get() == "Anglais"
        assert not tab.markdown_var.get()
        tab.input_text.insert("1.0", "bonjour")
        tab.target_language_var.set("")
        with patch("src.ia_multitools.ui.tabs.correction_tab.messagebox") as boxes:
            tab._correct_text()
        boxes.showerror.assert_called_once()
        assert service.correct_text.call_count == 1
    finally:
        notebook.destroy()


def test_translation_options_accessible_on_small_window(root):
    host = ttk.Toplevel(root)
    host.geometry("900x400")
    notebook = ttk.Notebook(host)
    notebook.pack(fill="both", expand=True)
    with patch.object(TranslationTab, "_get_service", return_value=Mock()):
        tab = TranslationTab(notebook, config_manager())
    notebook.add(tab.frame.container, text="Traduction")
    try:
        host.update()
        tab.frame._show_focused(SimpleNamespace(widget=tab.target_language_entry))
        host.update_idletasks()
        assert_inside(tab.target_language_entry, tab.frame.container)
        assert tab.frame.vscroll.winfo_ismapped()
    finally:
        host.destroy()
