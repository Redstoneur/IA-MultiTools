"""Shared native window icons and bundled asset lookup."""

import logging
from pathlib import Path
import sys
import tkinter as tk
from typing import Optional

logger = logging.getLogger(__name__)


def resolve_asset_path(filename: str) -> Optional[Path]:
    """Find assets in source checkouts and PyInstaller bundles."""
    directories = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        directories.append(Path(sys._MEIPASS) / "assets")
    directories.extend([
        Path(__file__).resolve().parents[3] / "assets",
        Path.cwd() / "assets",
    ])
    return next(
        (directory / filename for directory in directories
         if (directory / filename).is_file()),
        None,
    )


def apply_window_icon(window: tk.Tk | tk.Toplevel) -> None:
    """Set the current native icon and the default for future dialogs."""
    if window.tk.call("tk", "windowingsystem") == "win32":
        icon_path = resolve_asset_path("logo.ico")
        if icon_path:
            try:
                window.iconbitmap(default=str(icon_path))
                window.iconbitmap(str(icon_path))
                return
            except tk.TclError as exc:
                logger.warning("Impossible d'appliquer l'icone ICO: %s", exc)
        else:
            logger.warning("Icone logo.ico introuvable, utilisation du PNG")

    logo_path = resolve_asset_path("logo.png")
    if not logo_path:
        logger.warning("Icone logo.png introuvable")
        return
    try:
        image = tk.PhotoImage(master=window, file=str(logo_path))
        window.iconphoto(True, image)
        window._app_icon_image = image
    except tk.TclError as exc:
        logger.warning("Impossible d'appliquer l'icone PNG: %s", exc)
