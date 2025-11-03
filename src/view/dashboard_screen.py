from __future__ import annotations

import tkinter as tk


class DashboardScreen(tk.Frame):
    """Pantalla de inicio del sistema tras autenticación."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self._build_ui()

    def _build_ui(self) -> None:
        label = tk.Label(self, text="Bienvenido al Dashboard", font=("Segoe UI", 12, "bold"))
        label.pack(padx=20, pady=20)

