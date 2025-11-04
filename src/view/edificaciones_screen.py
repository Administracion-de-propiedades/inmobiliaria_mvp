# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, List

from core.frame_manager import BaseScreen
from view.widgets.base_table import BaseTable
from view.widgets.base_form import BaseForm
from services.edificacion_service import EdificacionService
from entities.edificacion import Edificacion


class EdificacionesScreen(BaseScreen):
    """
    ABM de Edificaciones aplicando el patrón BaseTable + BaseForm.
    Nota: la edición avanzada de terrenos asociados puede mantenerse en un
    selector aparte; aquí se muestra un resumen en modo lectura.
    """

    def __init__(self, parent, app: Any, *args: Any) -> None:
        super().__init__(parent)
        self.app = app
        self.svc = EdificacionService()
        self._selected_id: Optional[int] = None
        self._current_terrenos: List[int] = []

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
                ("tipo", "Tipo", 120),
                ("superficie_cubierta", "Sup. Cubierta (m²)", 160),
                ("terrenos", "Terrenos", 200),
            ],
            multiselect=False,
            height=18,
            on_select=self._on_select_table,
        )
        self.tbl.pack(fill="both", expand=True)

        # Formulario
        right = ttk.LabelFrame(self, text="Edificación", padding=10)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)

        self.form = BaseForm(right)
        self.form.grid(row=0, column=0, sticky="nsew")
        self.cb_tipo = self.form.add_combobox(
            "tipo",
            "Tipo:",
            ["CASA", "DUPLEX", "DEPARTAMENTO", "LOCAL", "GALPON"],
            readonly=True,
        )
        self.form.add_entry(
            "superficie_cubierta",
            "Sup. Cubierta (m²):",
            validator=self._valid_superficie,
        )
        # Campo informativo de terrenos asociados
        self.form.add_entry("terrenos_ids", "Terrenos (ids):")

        self.form.add_actions([
            ("Nuevo", self._nuevo),
            ("Guardar", self._guardar),
            ("Eliminar", self._eliminar),
            ("Volver", self._volver),
        ])

    # ---------------- Helpers ----------------
    def _valid_superficie(self, s: str) -> Optional[str]:
        if not s.strip():
            return None
        try:
            val = float((s or "").replace(",", "."))
            if val <= 0:
                return "La superficie debe ser > 0."
        except Exception:
            return "Sup. cubierta inválida."
        return None

    def _row_from_edificacion(self, e: Edificacion) -> tuple[str, list[Any]]:
        terrs = ",".join(str(t) for t in (e.terrenos_ids or []))
        sup = "" if e.superficie_cubierta is None else e.superficie_cubierta
        return (str(e.id), [e.tipo, sup, f"[{terrs}]"])

    def _load_table(self) -> None:
        rows: List[tuple[str, list[Any]]] = []
        for e in self.svc.listar():
            rows.append(self._row_from_edificacion(e))
        self.tbl.load_rows(rows)

    def _on_select_table(self, ids: list[str]) -> None:
        if not ids:
            return
        iid = int(ids[0])
        e = self.svc.obtener(iid)
        if not e:
            return
        self._selected_id = e.id
        self._current_terrenos = list(e.terrenos_ids or [])
        terrs_str = ",".join(str(t) for t in self._current_terrenos)
        self.form.set_values(
            {
                "tipo": e.tipo,
                "superficie_cubierta": e.superficie_cubierta if e.superficie_cubierta is not None else "",
                "terrenos_ids": f"[{terrs_str}]",
            }
        )

    def _collect_form(self) -> dict:
        data = self.form.get_values()
        out: dict[str, Any] = {}
        # sólo enviar campos presentes (merge en service.actualizar)
        t = data.get("tipo")
        if t:
            out["tipo"] = t
        sc = (data.get("superficie_cubierta") or "").strip()
        if sc:
            out["superficie_cubierta"] = float(sc.replace(",", "."))
        else:
            out["superficie_cubierta"] = None
        return out

    # ---------------- Acciones ----------------
    def _nuevo(self) -> None:
        self._selected_id = None
        self._current_terrenos = []
        self.form.clear()
        self.form.set_values({"tipo": "CASA"})

    def _guardar(self) -> None:
        if not self.form.validate():
            return
        try:
            data = self._collect_form()
            if self._selected_id:
                self.svc.actualizar(self._selected_id, data)
            else:
                # creación mínima
                self._selected_id = self.svc.crear(data)
            self._load_table()
            messagebox.showinfo("Éxito", "Edificación guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self) -> None:
        if not self._selected_id:
            messagebox.showwarning("Atención", "Seleccione una edificación.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la edificación seleccionada?"):
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
        """Hook on show."""
        pass

    def on_hide(self):  # noqa: D401
        """Hook on hide."""
        pass
