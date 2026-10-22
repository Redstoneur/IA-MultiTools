"""Native icons persist after mapping main windows and dialogs."""

import ctypes
import tkinter as tk
from unittest.mock import Mock, call, patch

import pytest
import ttkbootstrap as ttk

from src.ia_multitools.ui import branding
from src.ia_multitools.ui.first_run_wizard import FirstRunWizard
from src.ia_multitools.ui.main_window import MainWindow
from src.ia_multitools.ui.password_dialog import PasswordDialog
from src.ia_multitools.ui.settings_window import SettingsWindow
from .test_first_run_wizard import config_manager


def assert_native_icon(window):
    window.update()
    if window.tk.call("tk", "windowingsystem") == "win32":
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        send_message = user32.SendMessageW
        send_message.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t,
        ]
        send_message.restype = ctypes.c_ssize_t
        get_class_icon = user32.GetClassLongPtrW
        get_class_icon.argtypes = [ctypes.c_void_p, ctypes.c_int]
        get_class_icon.restype = ctypes.c_size_t
        frame = int(window.tk.call("wm", "frame", window), 0)
        # Windows falls back to the class icon for inherited defaults.
        assert send_message(frame, 0x007F, 0, 0) or get_class_icon(frame, -34)
        assert send_message(frame, 0x007F, 1, 0) or get_class_icon(frame, -14)
    else:
        assert window._app_icon_image.width() == 512


def test_main_window_icon(root):
    manager = config_manager()
    manager.get_config.return_value.first_run = False
    with (
        patch("src.ia_multitools.ui.main_window.ttk.Window", return_value=root),
        patch.object(MainWindow, "_build_ui"),
        patch.object(MainWindow, "_build_menu"),
    ):
        main = MainWindow(manager, Mock())
    assert main.logo_image.width() == 128
    assert_native_icon(root)


@pytest.mark.parametrize("factory", [
    lambda root: FirstRunWizard(root, config_manager()),
    lambda root: SettingsWindow(root, config_manager()),
    lambda root: PasswordDialog(root, Mock()),
])
def test_secondary_window_icons(root, factory):
    instance = factory(root)
    try:
        assert_native_icon(instance.window)
    finally:
        instance.window.destroy()


def test_default_icon_is_inherited_by_unconfigured_dialog(root):
    branding.apply_window_icon(root)
    dialog = ttk.Toplevel(root)
    try:
        if root.tk.call("tk", "windowingsystem") == "win32":
            assert_native_icon(dialog)
    finally:
        dialog.destroy()


def test_windows_uses_bundled_ico_for_current_and_future_windows(root):
    if root.tk.call("tk", "windowingsystem") != "win32":
        pytest.skip("Windows ICO handling")
    with patch.object(root, "iconbitmap", wraps=root.iconbitmap) as iconbitmap:
        branding.apply_window_icon(root)
    path = str(branding.resolve_asset_path("logo.ico"))
    assert iconbitmap.call_args_list == [call(default=path), call(path)]
    assert_native_icon(root)


def test_png_fallback_retains_image(root):
    original_resolver = branding.resolve_asset_path
    with patch.object(
        branding, "resolve_asset_path",
        side_effect=lambda name: None if name == "logo.ico" else original_resolver(name),
    ):
        branding.apply_window_icon(root)
    root.update()
    assert root._app_icon_image.width() == 512
    branding.apply_window_icon(root)


def test_bundle_assets_take_priority(tmp_path, monkeypatch):
    assets = tmp_path / "assets"
    assets.mkdir()
    icon = assets / "logo.ico"
    icon.touch()
    monkeypatch.setattr(branding.sys, "frozen", True, raising=False)
    monkeypatch.setattr(branding.sys, "_MEIPASS", str(tmp_path), raising=False)
    assert branding.resolve_asset_path("logo.ico") == icon


def test_invalid_ico_falls_back_to_png(root, caplog):
    original = root.iconbitmap
    with patch.object(root, "iconbitmap", side_effect=tk.TclError("invalid icon")):
        branding.apply_window_icon(root)
    assert "Impossible d'appliquer l'icone ICO" in caplog.text or (
        root.tk.call("tk", "windowingsystem") != "win32"
    )
    assert root._app_icon_image.width() == 512
    assert root.iconbitmap == original
    branding.apply_window_icon(root)
