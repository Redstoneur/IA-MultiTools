"""Settings parity and access to all tool controls on small windows."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import ttkbootstrap as ttk

from .test_first_run_wizard import config_manager, assert_inside
from src.ia_multitools.ui.settings_window import SettingsWindow
from src.ia_multitools.ui.tabs.definition_tab import DefinitionTab
from src.ia_multitools.ui.tabs.synonym_tab import SynonymTab
from src.ia_multitools.ui.tabs.correction_tab import CorrectionTab
from src.ia_multitools.ui.tabs.email_tab import EmailTab


@pytest.fixture
def settings(root):
    manager = config_manager()
    manager.validate.return_value = (True, [])
    instance = SettingsWindow(root, manager)
    instance.window.update()
    yield instance
    instance.window.destroy()


def test_settings_model_selection_and_connection_options(settings):
    settings.verify_ssl_var.set(False)
    settings.timeout_var.set("95")
    settings.temperature_var.set("0.7")
    with patch("src.ia_multitools.ui.settings_window.OpenAIClient") as factory:
        factory.return_value.list_models.return_value = ["b", "a", "b"]
        factory.return_value.test_connection.return_value = (True, "OK")
        settings._load_models()
        assert settings.model_entry["values"] == ("a", "b")
        assert settings.model_var.get() == "a"
        with patch("src.ia_multitools.ui.settings_window.messagebox"):
            assert settings._test_connection()
    assert factory.call_args.kwargs["verify_ssl"] is False
    assert factory.call_args.kwargs["temperature"] == 0.7
    assert factory.call_args.kwargs["timeout"] == 95
    assert factory.return_value.close.call_count == 2
    with (
        patch("src.ia_multitools.ui.settings_window.messagebox"),
        patch("src.ia_multitools.ui.settings_window.init_openai_client") as initialize,
    ):
        settings._save_settings()
    settings.config_manager.save_config.assert_called_once()
    assert initialize.call_args.kwargs["temperature"] == 0.7
    assert initialize.call_args.kwargs["timeout"] == 95
    assert initialize.call_args.kwargs["verify_ssl"] is False
    settings.api_key_var.set("different-key")
    assert not settings.model_entry["values"]
    assert settings._last_successful_test_signature is None


@pytest.mark.parametrize("geometry", ["600x400", "950x800"])
def test_all_settings_sections_scroll(settings, geometry):
    settings.window.geometry(geometry)
    settings.window.update()
    for tab_id in settings.notebook.tabs():
        settings.notebook.select(tab_id)
        settings.window.update()
        container = settings.notebook.nametowidget(tab_id)
        form = next(child for child in container.winfo_children()
                    if hasattr(child, "yview_moveto"))
        assert form.vscroll.winfo_ismapped()
        form.yview_moveto(1)
        settings.window.update_idletasks()
        last = form.winfo_children()[-1]
        assert_inside(last, container)
    buttons = settings.window.winfo_children()[0].winfo_children()[0].winfo_children()
    for button in buttons:
        assert_inside(button, settings.window)


def test_settings_ai_controls_visible_by_keyboard_and_wheel(settings):
    settings.window.geometry("600x400")
    settings.window.update()
    form = settings.ai_form
    for field in form.winfo_children():
        if isinstance(field, (ttk.Entry, ttk.Combobox, ttk.Spinbox, ttk.Button, ttk.Checkbutton)):
            form._show_focused(SimpleNamespace(widget=field))
            settings.window.update_idletasks()
            assert_inside(field, form.container)
    form.yview_moveto(0)
    form._on_mousewheel(SimpleNamespace(widget=form, delta=-120, num=0))
    settings.window.update_idletasks()
    assert form.vscroll.get()[0] > 0


@pytest.mark.parametrize("variable,value", [
    ("temperature_var", "nan"), ("temperature_var", "2.1"),
    ("timeout_var", "0"), ("timeout_var", "1.5"),
])
def test_invalid_settings_do_not_test_or_save(settings, variable, value):
    getattr(settings, variable).set(value)
    with (
        patch("src.ia_multitools.ui.settings_window.OpenAIClient") as factory,
        patch("src.ia_multitools.ui.settings_window.messagebox") as boxes,
    ):
        assert settings._test_connection() is False
        settings._save_settings()
    factory.assert_not_called()
    assert boxes.showerror.call_count == 2
    settings.config_manager.save_config.assert_not_called()


@pytest.mark.parametrize("tab_class,service_name", [
    (DefinitionTab, "definition_service"),
    (SynonymTab, "synonym_service"),
    (CorrectionTab, "text_correction_service"),
    (EmailTab, "email_correction_service"),
])
def test_tool_content_and_results_remain_accessible(root, tab_class, service_name):
    host = ttk.Toplevel(root)
    host.geometry("900x400")
    notebook = ttk.Notebook(host)
    notebook.pack(fill="both", expand=True)
    with patch(f"{tab_class.__module__}.get_{service_name}", return_value=Mock()):
        tab = tab_class(notebook, config_manager())
    notebook.add(tab.frame.container, text="Test")
    try:
        host.update()
        assert tab.frame.vscroll.winfo_ismapped()
        assert tab.frame.winfo_height() > tab.frame.container.winfo_height()
        tab.frame.yview_moveto(1)
        host.update_idletasks()
        assert tab.frame.vscroll.get()[0] > 0
        result_frame = tab.frame.winfo_children()[-1]
        assert result_frame.winfo_rooty() + result_frame.winfo_height() <= (
            tab.frame.container.winfo_rooty() + tab.frame.container.winfo_height()
        )
        first_input = getattr(tab, "term_entry", None) or getattr(tab, "word_entry", None)
        if first_input is None:
            first_input = tab.input_text
        tab.frame._show_focused(SimpleNamespace(widget=first_input))
        host.update_idletasks()
        assert_inside(first_input, tab.frame.container)
    finally:
        host.destroy()
