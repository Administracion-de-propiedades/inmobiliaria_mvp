from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from services.auth_service import AuthService


class LoginScreen(tk.Frame):
    """Pantalla de login con usuario y contraseña."""

    def __init__(self, master: tk.Misc, auth_service: AuthService, on_success: Callable[[], None]) -> None:
        super().__init__(master)
        self._auth_service = auth_service
        self._on_success = on_success
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        title = tk.Label(self, text="Iniciar Sesión", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        lbl_user = tk.Label(self, text="Usuario:")
        lbl_user.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.grid(row=1, column=1, sticky="we", padx=(5, 10), pady=5)

        lbl_pass = tk.Label(self, text="Contraseña:")
        lbl_pass.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=5)
        self.entry_pass = tk.Entry(self, show="•")
        self.entry_pass.grid(row=2, column=1, sticky="we", padx=(5, 10), pady=5)

        btn_login = tk.Button(self, text="Ingresar", command=self._on_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=(10, 10))

        # UX niceties
        self.entry_user.focus_set()
        self.entry_pass.bind("<Return>", lambda _e: self._on_login())

    def _on_login(self) -> None:
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()
        if self._auth_service.authenticate(username, password):
            self._on_success()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")

