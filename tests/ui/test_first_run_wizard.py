"""Layout regressions for the first-run configuration form."""

import tkinter as tk
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import ttkbootstrap as ttk

from src.ia_multitools.ui.first_run_wizard import FirstRunWizard
from src.ia_multitools.core.config_manager import AppConfig


MODULE = "src.ia_multitools.ui.first_run_wizard"


def config_manager():
    return Mock(get_config=Mock(return_value=AppConfig()))


@pytest.fixture(scope="module")
def root():
    try:
        window = ttk.Window()
    except tk.TclError as exc:
        if "no display name" in str(exc) or "couldn't connect to display" in str(exc):
            pytest.skip("A graphical display is required for layout tests")
        raise
    window.geometry("200x100")
    window.update()
    yield window
    window.destroy()


@pytest.fixture
def wizard(root):
    instance = FirstRunWizard(root, config_manager())
    yield instance
    instance.window.destroy()


def assert_inside(widget, container):
    assert widget.winfo_ismapped()
    assert widget.winfo_width() > 20
    assert widget.winfo_height() > 20
    assert widget.winfo_rootx() >= container.winfo_rootx()
    assert widget.winfo_rooty() >= container.winfo_rooty()
    assert (
        widget.winfo_rootx() + widget.winfo_width()
        <= container.winfo_rootx() + container.winfo_width()
    )
    assert (
        widget.winfo_rooty() + widget.winfo_height()
        <= container.winfo_rooty() + container.winfo_height()
    )


@pytest.mark.parametrize("geometry", ["500x400", "700x550", "900x760"])
def test_fields_scroll_and_actions_remain_visible(wizard, geometry):
    wizard.window.geometry(geometry)
    wizard.window.update()

    assert wizard.window.resizable() == (1, 1)
    for button in wizard.test_btn.master.winfo_children():
        assert_inside(button, wizard.window)

    for field in (
        wizard.model_entry, wizard.api_key_entry, wizard.base_url_entry,
        wizard.temperature_entry, wizard.timeout_entry, wizard.verify_ssl_check,
        wizard.models_btn,
    ):
        wizard._scroll_to_field(SimpleNamespace(widget=field))
        wizard.window.update_idletasks()
        assert_inside(field, wizard.form.container)

    assert wizard.form.vscroll.winfo_ismapped()
    assert wizard.model_entry.get() == "meta-llama-3.1-8b-instruct"
    wizard.model_entry.delete(0, tk.END)
    wizard.model_entry.insert(0, "test-model")
    assert wizard.model_entry.get() == "test-model"
    wizard.config_manager.save_config.assert_not_called()


def test_initial_size_fits_small_screen(root, monkeypatch):
    monkeypatch.setattr(ttk.Toplevel, "winfo_screenwidth", lambda self: 800)
    monkeypatch.setattr(ttk.Toplevel, "winfo_screenheight", lambda self: 600)
    wizard = FirstRunWizard(root, config_manager())
    wizard.window.update()

    assert wizard.window.winfo_width() <= 800 - 80
    assert wizard.window.winfo_height() <= 600 - 100
    assert wizard.window.winfo_x() >= 0
    assert wizard.window.winfo_y() >= 0
    assert_inside(wizard.save_btn, wizard.window)
    wizard.window.destroy()


def test_defaults_match_config(wizard):
    config = wizard.config_manager.get_config().ai
    assert wizard._get_ai_signature() == (
        config.base_url, config.model, config.api_key,
        config.temperature, config.timeout, True,
    )


@pytest.mark.parametrize("verify_ssl", [True, False])
def test_models_use_current_connection_settings(wizard, verify_ssl):
    wizard.verify_ssl_var.set(verify_ssl)
    wizard.timeout_var.set("120")
    wizard.temperature_var.set("0.7")
    wizard.api_key_var.set("test-key")
    with patch(f"{MODULE}.OpenAIClient") as factory:
        factory.return_value.list_models.return_value = ["model-b", "model-a", "model-b"]
        wizard._load_models()

    factory.assert_called_once_with(
        api_key="test-key", base_url=wizard.base_url_var.get(),
        model="meta-llama-3.1-8b-instruct", temperature=0.7,
        timeout=120, verify_ssl=verify_ssl,
    )
    assert wizard.model_entry["values"] == ("model-a", "model-b")
    assert wizard.model_var.get() == "model-a"
    factory.return_value.close.assert_called_once()
    assert str(wizard.save_btn["state"]) == "disabled"


def test_model_refresh_preserves_selection_and_allows_manual_input(wizard):
    wizard.model_var.set("model-b")
    with patch(f"{MODULE}.OpenAIClient") as factory:
        factory.return_value.list_models.return_value = ["model-a", "model-b"]
        wizard._load_models()
    assert wizard.model_var.get() == "model-b"
    wizard.model_var.set("manual-model")
    assert wizard._get_ai_signature()[1] == "manual-model"


@pytest.mark.parametrize("variable,value", [
    ("base_url_var", "http://localhost:8080/v1"),
    ("api_key_var", "new-key"),
    ("verify_ssl_var", False),
])
def test_connection_changes_clear_model_list(wizard, variable, value):
    wizard.model_entry.configure(values=("old-model",))
    getattr(wizard, variable).set(value)
    assert not wizard.model_entry["values"]


@pytest.mark.parametrize("failure", [False, True])
def test_model_errors_are_visible_and_client_is_closed(wizard, failure):
    with patch(f"{MODULE}.OpenAIClient") as factory, patch(f"{MODULE}.messagebox") as boxes:
        factory.return_value.list_models.return_value = []
        if failure:
            factory.return_value.list_models.side_effect = RuntimeError("unavailable")
        wizard._load_models()
    assert boxes.showerror.called if failure else boxes.showwarning.called
    factory.return_value.close.assert_called_once()
    assert str(wizard.models_btn["state"]) == "normal"


@pytest.mark.parametrize("variable,value", [
    ("temperature_var", "-0.1"), ("temperature_var", "2.1"),
    ("temperature_var", "nan"), ("temperature_var", "abc"),
    ("timeout_var", "0"), ("timeout_var", "-1"),
    ("timeout_var", "1.5"), ("timeout_var", ""),
])
def test_invalid_settings_do_not_make_requests(wizard, variable, value):
    getattr(wizard, variable).set(value)
    with patch(f"{MODULE}.OpenAIClient") as factory, patch(f"{MODULE}.messagebox") as boxes:
        wizard._test_connection()
        wizard._load_models()
        wizard._save_and_continue()
    factory.assert_not_called()
    assert boxes.showerror.call_count == 3
    wizard.config_manager.save_config.assert_not_called()


def test_connection_test_and_save_use_all_settings(wizard):
    wizard.verify_ssl_var.set(False)
    wizard.temperature_var.set("1.2")
    wizard.timeout_var.set("95")
    with (
        patch(f"{MODULE}.OpenAIClient") as factory,
        patch(f"{MODULE}.messagebox"),
        patch("src.ia_multitools.core.openai_client.init_openai_client") as initialize,
        patch.object(wizard, "_close") as close,
    ):
        factory.return_value.simple_completion.return_value = "OK"
        wizard._test_connection()
        factory.assert_called_once_with(
            api_key="sk-dummy", base_url=wizard.base_url_var.get(),
            model=wizard.model_var.get(), temperature=1.2, timeout=95, verify_ssl=False,
        )
        factory.return_value.close.assert_called_once()
        assert str(wizard.save_btn["state"]) == "normal"
        wizard._save_and_continue()

    config = wizard.config_manager.get_config()
    assert (config.ai.temperature, config.ai.timeout, config.ai.verify_ssl) == (1.2, 95, False)
    assert not config.first_run
    wizard.config_manager.save_config.assert_called_once()
    assert initialize.call_args.kwargs["verify_ssl"] is False
    assert initialize.call_args.kwargs["timeout"] == 95
    assert initialize.call_args.kwargs["temperature"] == 1.2
    close.assert_called_once()


@pytest.mark.parametrize("variable,value", [
    ("temperature_var", "0.9"), ("timeout_var", "120"), ("verify_ssl_var", False),
    ("model_var", "different-model"),
])
def test_changing_settings_requires_another_test(wizard, variable, value):
    wizard._last_successful_test_signature = wizard._get_ai_signature()
    wizard.save_btn.configure(state="normal")
    getattr(wizard, variable).set(value)
    assert wizard._last_successful_test_signature is None
    assert str(wizard.save_btn["state"]) == "disabled"
    with patch(f"{MODULE}.messagebox") as boxes:
        wizard._save_and_continue()
    boxes.showerror.assert_called_once()
    wizard.config_manager.save_config.assert_not_called()
