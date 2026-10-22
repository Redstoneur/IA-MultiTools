"""Scrollable forms with keyboard access to off-screen controls."""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame


class ScrollableForm(ScrolledFrame):
    """Keep notebook content scrollable without shrinking its controls."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, autohide=False, **kwargs)
        self.bind("<Map>", self._bind_focus, "+")
        self.bind("<Configure>", self._wrap_labels, "+")
        self.bind("<Configure>", self._refresh_scroll, "+")

    def _refresh_scroll(self, _event=None):
        first, last = self.vscroll.get()
        if first > 0 and last >= 0.999:
            self.yview_moveto(1)
        else:
            self.yview()

    def _wrap_labels(self, _event=None):
        def wrap_children(widget):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Label) and child.cget("wraplength"):
                    width = max(1, child.master.winfo_width() - 40)
                    if child.winfo_manager() == "grid":
                        column = int(child.grid_info()["column"])
                        width = max(1, child.master.grid_bbox(column, 0)[2] - 20)
                    child.configure(wraplength=width)
                wrap_children(child)
        wrap_children(self)

    def _on_mousewheel(self, event):
        # Let text editors scroll their contents before moving the whole form.
        if isinstance(event.widget, tk.Text):
            first, last = event.widget.yview()
            upwards = event.delta > 0 or event.num == 4
            if (upwards and first > 0) or (not upwards and last < 1):
                return None
        super()._on_mousewheel(event)
        return "break"

    def _bind_focus(self, _event=None):
        def bind_children(widget):
            for child in widget.winfo_children():
                child.bind("<FocusIn>", self._show_focused, "+")
                bind_children(child)
        bind_children(self)

    def _show_focused(self, event: tk.Event):
        field = event.widget
        top = self.container.winfo_rooty()
        bottom = top + self.container.winfo_height()
        if field.winfo_rooty() < top or field.winfo_rooty() + field.winfo_height() > bottom:
            offset = field.winfo_rooty() - self.winfo_rooty()
            self.yview_moveto(max(0, offset - 10) / max(1, self.winfo_height()))
