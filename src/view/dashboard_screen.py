from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional


class DashboardScreen(tk.Frame):
    """Pantalla de inicio del sistema tras autenticación."""

    def __init__(self, master: tk.Misc, app: Optional[object] = None) -> None:
        super().__init__(master)
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        label = ttk.Label(self, text="Bienvenido al Dashboard", font=("Segoe UI", 12, "bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=0, pady=10)

        # Botón para abrir Edificaciones
        from view.edificaciones_screen import EdificacionesScreen

        ttk.Button(
            btns,
            text="Edificaciones",
            command=lambda: hasattr(self.app, "show_screen") and self.app.show_screen(EdificacionesScreen),
        ).grid(row=0, column=0, padx=6)

        # Opcional: botón a Terrenos si existe
        try:
            from view.terrenos_screen import TerrenosScreen  # noqa: F401

            ttk.Button(
                btns,
                text="Terrenos",
                command=lambda: hasattr(self.app, "show_screen") and self.app.show_screen(TerrenosScreen),
            ).grid(row=0, column=1, padx=6)
        except Exception:
            pass

        # Opcional: botón a Loteos si existe
        try:
            from view.loteos_screen import LoteosScreen  # noqa: F401

            ttk.Button(
                btns,
                text="Loteos",
                command=lambda: hasattr(self.app, "show_screen") and self.app.show_screen(LoteosScreen),
            ).grid(row=0, column=2, padx=6)
        except Exception:
            pass

