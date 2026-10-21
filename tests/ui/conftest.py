"""A single Tk interpreter for graphical tests and ttkbootstrap styles."""

import tkinter as tk

import pytest
import ttkbootstrap as ttk


@pytest.fixture(scope="session")
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
