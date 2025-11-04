# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from core.frame_manager import BaseScreen

# Importar pantallas destino (tolerante si alguna falta)
try:  # Usuarios puede no existir aún
    from view.usuarios_screen import UsuariosScreen  # type: ignore
except Exception:  # pragma: no cover - interfaz opcional
    UsuariosScreen = None  # type: ignore[assignment]

try:
    from view.terrenos_screen import TerrenosScreen  # type: ignore
except Exception:  # pragma: no cover
    TerrenosScreen = None  # type: ignore[assignment]

try:
    from view.edificaciones_screen import EdificacionesScreen  # type: ignore
except Exception:  # pragma: no cover
    EdificacionesScreen = None  # type: ignore[assignment]

try:
    from view.loteos_screen import LoteosScreen  # type: ignore
except Exception:  # pragma: no cover
    LoteosScreen = None  # type: ignore[assignment]

try:
    from view.reservas_screen import ReservasScreen  # type: ignore
except Exception:  # pragma: no cover
    ReservasScreen = None  # type: ignore[assignment]


class DashboardScreen(BaseScreen):
    """
    Pantalla principal (Dashboard) del sistema.
    Permite navegar a los distintos módulos del sistema.
    """

    def __init__(self, parent, app: Any, *args: Any) -> None:
        super().__init__(parent)
        self.app = app

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self, padding=40)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ttk.Label(frame, text="🏠 Panel Principal – Inmobiliaria MVP", font=("Segoe UI", 20, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 30))

        # Botonera principal
        buttons = [
            ("👤 Usuarios", self._open_usuarios),
            ("📋 Terrenos", self._open_terrenos),
            ("🏗️ Edificaciones", self._open_edificaciones),
            ("🌐 Loteos", self._open_loteos),
            ("🧾 Reservas", self._open_reservas),
            ("🚪 Cerrar sesión", self._logout),
        ]

        for i, (label, cmd) in enumerate(buttons):
            ttk.Button(frame, text=label, command=cmd, width=25).grid(row=1 + i, column=0, pady=6, sticky="ew")

        footer = ttk.Label(
            frame,
            text="© 2025 - Sistema de Administración de Propiedades",
            font=("Segoe UI", 9),
        )
        footer.grid(row=len(buttons) + 2, column=0, pady=(30, 0))

    # --- Navegación ---
    def _open_usuarios(self) -> None:
        try:
            if UsuariosScreen is not None:
                self.app.show_screen(UsuariosScreen)
        except Exception as e:  # pragma: no cover - feedback visual
            print(f"Error abriendo UsuariosScreen: {e}")

    def _open_terrenos(self) -> None:
        try:
            if TerrenosScreen is not None:
                self.app.show_screen(TerrenosScreen)
        except Exception as e:  # pragma: no cover
            print(f"Error abriendo TerrenosScreen: {e}")

    def _open_edificaciones(self) -> None:
        try:
            if EdificacionesScreen is not None:
                self.app.show_screen(EdificacionesScreen)
        except Exception as e:  # pragma: no cover
            print(f"Error abriendo EdificacionesScreen: {e}")

    def _open_loteos(self) -> None:
        try:
            if LoteosScreen is not None:
                self.app.show_screen(LoteosScreen)
        except Exception as e:  # pragma: no cover
            print(f"Error abriendo LoteosScreen: {e}")

    def _open_reservas(self) -> None:
        try:
            if ReservasScreen is not None:
                self.app.show_screen(ReservasScreen)
        except Exception as e:  # pragma: no cover
            print(f"Error abriendo ReservasScreen: {e}")

    def _logout(self) -> None:
        """Volver al login."""
        from view.login_screen import LoginScreen

        if hasattr(self.app, "router"):
            self.app.router.replace(LoginScreen)
        else:
            self.app.show_screen(LoginScreen)

    # --- Hooks opcionales ---
    def on_show(self, *args, **kwargs):  # noqa: D401
        """Hook: se llama cuando el dashboard se vuelve visible."""
        pass

    def on_hide(self):  # noqa: D401
        """Hook: se llama cuando se oculta el dashboard."""
        pass

