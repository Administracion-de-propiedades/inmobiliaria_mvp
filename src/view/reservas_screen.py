# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, List, Tuple, Optional

from core.frame_manager import BaseScreen
from view.widgets.base_table import BaseTable
from view.widgets.base_form import BaseForm
from services.reserva_service import ReservaService
from services.terreno_service import TerrenoService
from services.edificacion_service import EdificacionService


class ReservasScreen(BaseScreen):
    """
    ABM de Reservas polimórficas (TERRENO o EDIFICACION) usando BaseTable y BaseForm.
    - Listado (BaseTable)
    - Formulario con selector de tipo y propiedad (BaseForm)
    - Acciones: Nuevo, Guardar, Confirmar, Cancelar, Eliminar, Volver
    """

    def __init__(self, parent, app: Any, *args: Any) -> None:
        super().__init__(parent)
        self.app = app
        self.rsvc = ReservaService()
        self.tsvc = TerrenoService()
        self.esvc = EdificacionService()

        self.selected_id: Optional[int] = None
        self._cache_prop: List[Tuple[int, str]] = []  # (id, etiqueta "ID | ...")

        self._build_ui()
        self._load_propiedades_cache()
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
                ("tipo", "Tipo", 100),
                ("prop", "Propiedad", 160),
                ("cliente", "Cliente", 160),
                ("fecha", "Fecha", 110),
                ("monto", "Monto", 110),
                ("estado", "Estado", 110),
            ],
            multiselect=False,
            height=18,
            on_select=self._on_select_table,
        )
        self.tbl.pack(fill="both", expand=True)

        # Formulario
        right = ttk.LabelFrame(self, text="Datos de la Reserva", padding=10)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.form = BaseForm(right)
        self.cb_tipo = self.form.add_combobox(
            "tipo_propiedad",
            "Tipo:",
            ["TERRENO", "EDIFICACION"],
            readonly=True,
        )
        # Propiedad dinámica
        self.cb_prop = self.form.add_combobox(
            "propiedad_id",
            "Propiedad:",
            values=[],
            readonly=True,
            validator=lambda s: None if self._label_to_id(s) else "Seleccione una propiedad.",
        )
        self.form.add_entry("cliente", "Cliente:")
        self.form.add_entry("fecha_reserva", "Fecha (YYYY-MM-DD):")
        self.form.add_entry(
            "monto_reserva",
            "Monto:",
            validator=lambda s: self._valid_monto(s),
        )
        self.form.add_combobox(
            "estado",
            "Estado:",
            ["ACTIVA", "CANCELADA", "CONFIRMADA"],
            readonly=True,
        )
        self.form.add_entry("observaciones", "Observaciones:")

        actions = ttk.Frame(right)
        actions.grid(row=99, column=0, columnspan=2, pady=(10, 0), sticky="w")
        ttk.Button(actions, text="Nuevo", command=self._nuevo).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Guardar", command=self._guardar).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Eliminar", command=self._eliminar).grid(row=0, column=2, padx=4)
        ttk.Button(actions, text="Volver", command=self._volver).grid(row=0, column=5, padx=4)

        # Acciones de estado
        state_bar = ttk.Frame(right)
        state_bar.grid(row=100, column=0, columnspan=2, pady=(6, 0), sticky="w")
        ttk.Button(state_bar, text="Confirmar", command=self._confirmar).grid(row=0, column=0, padx=4)
        ttk.Button(state_bar, text="Cancelar", command=self._cancelar).grid(row=0, column=1, padx=4)

        # Bind cambios de tipo
        self.cb_tipo.bind("<<ComboboxSelected>>", lambda _e: self._load_propiedades_cache())

    # ------------- Data helpers -------------
    def _valid_monto(self, s: str) -> Optional[str]:
        try:
            val = float((s or "").replace(",", "."))
            if val <= 0:
                return "El monto de reserva debe ser positivo."
        except Exception:
            return "Monto inválido."
        return None

    def _load_propiedades_cache(self) -> None:
        tipo = self.form.get_values().get("tipo_propiedad") or "TERRENO"
        self._cache_prop.clear()
        labels: List[str] = []
        try:
            if tipo == "TERRENO":
                for t in self.tsvc.listar():
                    lab = f"{t.id} | Mz {t.manzana} · Lote {t.numero_lote} · {t.superficie} m²"
                    if t.id is not None:
                        self._cache_prop.append((int(t.id), lab))
                        labels.append(lab)
            else:
                for e in self.esvc.listar():
                    terrs = ",".join(str(x) for x in (e.terrenos_ids or []))
                    sup = "" if e.superficie_cubierta is None else f"{e.superficie_cubierta} m²"
                    lab = f"{e.id} | {e.tipo} {sup} · Terrenos [{terrs}]"
                    if e.id is not None:
                        self._cache_prop.append((int(e.id), lab))
                        labels.append(lab)
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron cargar propiedades: {ex}")
            labels = []
        self.cb_prop["values"] = labels
        self.form.set_values({"propiedad_id": ""})

    def _label_to_id(self, label: str) -> Optional[int]:
        try:
            return int(label.split("|", 1)[0].strip()) if label else None
        except Exception:
            return None

    def _row_from_reserva(self, r) -> tuple[str, list[Any]]:
        prop_txt = f"{r.tipo_propiedad} #{r.propiedad_id}"
        return (
            str(r.id),
            [r.tipo_propiedad, prop_txt, r.cliente, r.fecha_reserva, r.monto_reserva, r.estado],
        )

    def _load_table(self) -> None:
        rows: List[tuple[str, list[Any]]] = []
        for r in self.rsvc.listar():
            rows.append(self._row_from_reserva(r))
        self.tbl.load_rows(rows)

    def _on_select_table(self, ids: list[str]) -> None:
        if not ids:
            return
        rid = int(ids[0])
        r = self.rsvc.obtener(rid)
        if not r:
            return
        self.selected_id = r.id
        self.form.set_values(
            {
                "tipo_propiedad": r.tipo_propiedad,
                "cliente": r.cliente,
                "fecha_reserva": r.fecha_reserva,
                "monto_reserva": r.monto_reserva,
                "estado": r.estado,
                "observaciones": r.observaciones or "",
            }
        )
        # recargar opciones de propiedades y fijar label
        self._load_propiedades_cache()
        for _id, lab in self._cache_prop:
            if _id == r.propiedad_id:
                self.form.set_values({"propiedad_id": lab})
                break

    def _collect_form(self) -> dict:
        data = self.form.get_values()
        tipo = data.get("tipo_propiedad") or "TERRENO"
        prop_id = self._label_to_id(data.get("propiedad_id") or "")
        if not prop_id:
            raise ValueError("Debe seleccionar una propiedad.")
        try:
            monto = float(str(data.get("monto_reserva") or "0").replace(",", "."))
        except Exception:
            raise ValueError("Monto inválido.")
        if monto <= 0:
            raise ValueError("El monto de reserva debe ser positivo.")
        return {
            "tipo_propiedad": tipo,
            "propiedad_id": int(prop_id),
            "cliente": str(data.get("cliente") or "").strip(),
            "fecha_reserva": str(data.get("fecha_reserva") or "").strip(),
            "monto_reserva": monto,
            "estado": str(data.get("estado") or "ACTIVA"),
            "observaciones": (str(data.get("observaciones") or "").strip() or None),
        }

    # ------------- Acciones -------------
    def _nuevo(self) -> None:
        self.selected_id = None
        self.form.clear()
        self.form.set_values({"tipo_propiedad": "TERRENO", "estado": "ACTIVA"})
        self._load_propiedades_cache()

    def _guardar(self) -> None:
        if not self.form.validate():
            return
        try:
            datos = self._collect_form()
            if self.selected_id:
                self.rsvc.actualizar(self.selected_id, datos)
            else:
                self.selected_id = self.rsvc.crear(datos)
            self._load_table()
            messagebox.showinfo("Éxito", "Reserva guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _confirmar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return
        try:
            self.rsvc.confirmar(self.selected_id)
            self._load_table()
            self.form.set_values({"estado": "CONFIRMADA"})
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _cancelar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return
        try:
            self.rsvc.cancelar(self.selected_id)
            self._load_table()
            self.form.set_values({"estado": "CANCELADA"})
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la reserva seleccionada?"):
            return
        try:
            self.rsvc.eliminar(self.selected_id)
            self._nuevo()
            self._load_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self) -> None:
        if hasattr(self.app, "go_back"):
            self.app.go_back()
        elif hasattr(self.app, "show_dashboard"):
            self.app.show_dashboard()

    # --- Hooks ---
    def on_show(self, *args, **kwargs):  # noqa: D401
        """Hook on show."""
        pass

    def on_hide(self):  # noqa: D401
        """Hook on hide."""
        pass

