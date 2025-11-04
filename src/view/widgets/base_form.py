# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional, Callable

Validator = Callable[[str], Optional[str]]  # recibe texto, devuelve msg de error o None


class BaseForm(ttk.Frame):
    """
    Form base con:
    - Helper para crear filas label+entry/combobox/check
    - get_values()/set_values() con dict
    - Validación declarativa por campo
    - Barra de botones estándar
    """

    def __init__(self, parent: tk.Widget, title: Optional[str] = None) -> None:
        super().__init__(parent)
        self._vars: Dict[str, tk.Variable] = {}
        self._validators: Dict[str, Validator] = {}

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        if title:
            ttk.Label(self, text=title, font=("Segoe UI", 12, "bold")).grid(
                row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
            )
            self._next_row = 1
        else:
            self._next_row = 0

        # zona para mensajes de error/info (se muestra bajo demanda)
        self._msg = ttk.Label(self, text="", foreground="#b00020")

    # ---------- Creación de campos ----------
    def add_entry(self, name: str, label: str, width: int = 28, validator: Optional[Validator] = None) -> tk.Entry:
        ttk.Label(self, text=label).grid(row=self._next_row, column=0, sticky="e", pady=3, padx=(0, 4))
        var = tk.StringVar()
        self._vars[name] = var
        if validator:
            self._validators[name] = validator
        entry = ttk.Entry(self, textvariable=var, width=width)
        entry.grid(row=self._next_row, column=1, sticky="we", pady=3)
        self._next_row += 1
        return entry

    def add_combobox(
        self,
        name: str,
        label: str,
        values: list[str],
        width: int = 26,
        validator: Optional[Validator] = None,
        readonly: bool = True,
    ) -> ttk.Combobox:
        ttk.Label(self, text=label).grid(row=self._next_row, column=0, sticky="e", pady=3, padx=(0, 4))
        var = tk.StringVar()
        self._vars[name] = var
        if validator:
            self._validators[name] = validator
        cb = ttk.Combobox(self, textvariable=var, values=values, state="readonly" if readonly else "normal", width=width)
        cb.grid(row=self._next_row, column=1, sticky="w", pady=3)
        self._next_row += 1
        return cb

    def add_check(self, name: str, label: str) -> ttk.Checkbutton:
        var = tk.BooleanVar(value=False)
        self._vars[name] = var
        chk = ttk.Checkbutton(self, text=label, variable=var)
        chk.grid(row=self._next_row, column=1, sticky="w", pady=3)
        ttk.Label(self, text="").grid(row=self._next_row, column=0)  # placeholder
        self._next_row += 1
        return chk

    def add_text(self, name: str, label: str, width: int = 28) -> ttk.Entry:
        # alias simple (usa Entry)
        return self.add_entry(name, label, width=width)

    # ---------- Valores ----------
    def get_values(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for k, var in self._vars.items():
            data[k] = var.get()
        return data

    def set_values(self, data: Dict[str, Any]) -> None:
        for k, v in (data or {}).items():
            if k in self._vars:
                self._vars[k].set(v if v is not None else "")

    def clear(self) -> None:
        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set("")
        self.hide_message()

    # ---------- Validación ----------
    def validate(self) -> bool:
        for name, validator in self._validators.items():
            val = self._vars[name].get()
            err = validator(val)
            if err:
                self.show_error(err)
                return False
        self.hide_message()
        return True

    def show_error(self, msg: str) -> None:
        self._msg.configure(text=msg, foreground="#b00020")
        self._msg.grid(row=self._next_row, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def show_info(self, msg: str) -> None:
        self._msg.configure(text=msg, foreground="#0a7")
        self._msg.grid(row=self._next_row, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def hide_message(self) -> None:
        self._msg.configure(text="")
        self._msg.grid_forget()

    # ---------- Botonera ----------
    def add_actions(self, actions: list[tuple[str, Callable[[], None]]]) -> ttk.Frame:
        bar = ttk.Frame(self)
        bar.grid(row=self._next_row + 1, column=0, columnspan=2, pady=(8, 0))
        for i, (label, cmd) in enumerate(actions):
            ttk.Button(bar, text=label, command=cmd).grid(row=0, column=i, padx=4)
        return bar

