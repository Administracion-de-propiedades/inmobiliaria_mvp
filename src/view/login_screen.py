# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from services.auth_service import AuthService


class LoginScreen(tk.Frame):
    """
    Pantalla de inicio de sesión del sistema.
    Permite ingresar usuario y contraseña, valida con AuthService,
    y llama a un callback on_login_success(user) si la autenticación es válida.
    """

    def __init__(
        self,
        parent: tk.Misc,
        auth_service: Optional[AuthService] = None,
        on_success: Optional[Callable[..., None]] = None,
        app: Optional[object] = None,
    ) -> None:
        super().__init__(parent)
        self.auth = auth_service or AuthService()
        self._on_success = on_success
        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.error_var = tk.StringVar()

        self._build_ui()
        self._configure_events()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ttk.Frame(self, padding=30)
        container.grid(row=0, column=0, sticky="nsew")

        # Título con codificación correcta
        label_title = ttk.Label(container, text="Iniciar Sesión", font=("Arial", 18, "bold"))
        label_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(container, text="Usuario:").grid(row=1, column=0, sticky="e", pady=5)
        ttk.Entry(container, textvariable=self.username_var, width=25).grid(row=1, column=1, sticky="w")

        ttk.Label(container, text="Contraseña:").grid(row=2, column=0, sticky="e", pady=5)
        entry_pass = ttk.Entry(container, textvariable=self.password_var, show="*", width=25)
        entry_pass.grid(row=2, column=1, sticky="w")

        ttk.Button(container, text="Ingresar", command=self._do_login).grid(row=3, column=0, columnspan=2, pady=15)

        label_error = ttk.Label(container, textvariable=self.error_var, foreground="red")
        label_error.grid(row=4, column=0, columnspan=2)

        self.username_var.set("")
        self.password_var.set("")
        entry_pass.bind("<Return>", lambda _e: self._do_login())

    def _configure_events(self) -> None:
        self.bind("<Visibility>", lambda _e: self.username_var.set(""))
        self.bind("<Visibility>", lambda _e: self.password_var.set(""))

    def _do_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.error_var.set("Debe ingresar usuario y contraseña.")
            return

        user = self.auth.authenticate(username, password)
        if user:
            self.error_var.set("")
            # Navegar al dashboard según manejador disponible
            if self._on_success is not None:
                try:
                    self._on_success(user)
                except TypeError:
                    self._on_success()
            elif self.app is not None and hasattr(self.app, "show_dashboard"):
                # type: ignore[attr-defined]
                self.app.show_dashboard(user)
            elif self.app is not None and hasattr(self.app, "show_screen"):
                from view.dashboard_screen import DashboardScreen

                self.app.show_screen(DashboardScreen, user)  # type: ignore[attr-defined]
        else:
            self.error_var.set("Usuario o contraseña inválidos.")

