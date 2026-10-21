"""Layout regressions for the first-run configuration form."""

import tkinter as tk
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import ttkbootstrap as ttk

from src.ia_multitools.ui.first_run_wizard import FirstRunWizard


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
    instance = FirstRunWizard(root, Mock())
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

    for field in (wizard.model_entry, wizard.api_key_entry, wizard.base_url_entry):
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
    wizard = FirstRunWizard(root, Mock())
    wizard.window.update()

    assert wizard.window.winfo_width() <= 800 - 80
    assert wizard.window.winfo_height() <= 600 - 100
    assert wizard.window.winfo_x() >= 0
    assert wizard.window.winfo_y() >= 0
    assert_inside(wizard.save_btn, wizard.window)
    wizard.window.destroy()
