# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, List

from core.frame_manager import BaseScreen
from view.widgets.base_table import BaseTable
from view.widgets.base_form import BaseForm
from services.terreno_service import TerrenoService
from entities.terreno import Terreno


class TerrenosScreen(BaseScreen):
    """
    ABM de Terrenos, refactorizado para usar BaseTable y BaseForm.
    """

    def __init__(self, parent, app: Any, *args: Any) -> None:
        super().__init__(parent)
        self.app = app
        self.svc = TerrenoService()
        self._selected_id: Optional[int] = None

        self._build_ui()
        self._load_table()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Tabla
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tbl = BaseTable(
            parent=left,
            columns=[
                ("manzana", "Manzana", 100),
                ("lote", "Lote", 90),
                ("superficie", "Superficie (m²)", 140),
                ("nomenclatura", "Nomenclatura", 180),
            ],
            multiselect=False,
            height=18,
            on_select=self._on_select_table,
        )
        self.tbl.pack(fill="both", expand=True)

        # Formulario
        right = ttk.LabelFrame(self, text="Terreno", padding=10)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)

        self.form = BaseForm(right)
        self.form.grid(row=0, column=0, sticky="nsew")
        self.form.add_entry("manzana", "Manzana:")
        self.form.add_entry("numero_lote", "Lote:")
        self.form.add_entry("superficie", "Superficie (m²):", validator=self._valid_superficie)
        self.form.add_entry("nomenclatura", "Nomenclatura:")
        self.form.add_actions([
            ("Nuevo", self._nuevo),
            ("Guardar", self._guardar),
            ("Eliminar", self._eliminar),
            ("Volver", self._volver),
        ])

    # ---------------- Helpers ----------------
    def _valid_superficie(self, s: str) -> Optional[str]:
        try:
            val = float((s or "").replace(",", "."))
            if val <= 0:
                return "La superficie debe ser > 0."
        except Exception:
            return "Superficie inválida."
        return None

    def _row_from_terreno(self, t: Terreno) -> tuple[str, list[Any]]:
        return (str(t.id), [t.manzana, t.numero_lote, t.superficie, t.nomenclatura or ""])

    def _load_table(self) -> None:
        rows: List[tuple[str, list[Any]]] = []
        for t in self.svc.listar():
            rows.append(self._row_from_terreno(t))
        self.tbl.load_rows(rows)

    def _on_select_table(self, ids: list[str]) -> None:
        if not ids:
            return
        iid = int(ids[0])
        t = self.svc.obtener(iid)
        if not t:
            return
        self._selected_id = t.id
        self.form.set_values(
            {
                "manzana": t.manzana or "",
                "numero_lote": t.numero_lote or "",
                "superficie": t.superficie,
                "nomenclatura": t.nomenclatura or "",
            }
        )

    def _collect_form(self) -> dict:
        data = self.form.get_values()
        data["superficie"] = float(str(data["superficie"]).replace(",", ".") or 0)
        return data

    # ---------------- Acciones ----------------
    def _nuevo(self) -> None:
        self._selected_id = None
        self.form.clear()

    def _guardar(self) -> None:
        if not self.form.validate():
            return
        try:
            data = self._collect_form()
            if self._selected_id:
                self.svc.actualizar(self._selected_id, data)
            else:
                self._selected_id = self.svc.crear(data)
            self._load_table()
            messagebox.showinfo("Éxito", "Terreno guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self) -> None:
        if not self._selected_id:
            messagebox.showwarning("Atención", "Seleccione un terreno.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el terreno seleccionado?"):
            return
        try:
            self.svc.eliminar(self._selected_id)
            self._nuevo()
            self._load_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self) -> None:
        if hasattr(self.app, "go_back"):
            self.app.go_back()
        elif hasattr(self.app, "show_dashboard"):
            self.app.show_dashboard()

    # ---------------- Hooks ----------------
    def on_show(self, *args, **kwargs):  # noqa: D401
        """Hook on show: refresh if needed."""
        pass

    def on_hide(self):  # noqa: D401
        """Hook on hide."""
        pass
