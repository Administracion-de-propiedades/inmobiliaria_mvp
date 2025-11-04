# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional

from services.reserva_service import ReservaService
from services.terreno_service import TerrenoService
from services.edificacion_service import EdificacionService
from entities.reserva import Reserva


class ReservasScreen(tk.Frame):
    """
    ABM de Reservas polimórficas (TERRENO o EDIFICACION).
    - Listado (Treeview)
    - Formulario con selector de tipo y propiedad
    - Acciones: Nuevo, Guardar (crear/editar), Confirmar, Cancelar, Eliminar, Volver
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.rsvc = ReservaService()
        self.tsvc = TerrenoService()
        self.esvc = EdificacionService()

        self.selected_id: Optional[int] = None
        self._cache_prop: List[Tuple[int, str]] = []  # (id, etiqueta "ID | ...")

        self.vars = {
            "tipo_propiedad": tk.StringVar(value="TERRENO"),
            "propiedad_id": tk.StringVar(),  # guarda el label; se parsea a id
            "cliente": tk.StringVar(),
            "fecha_reserva": tk.StringVar(),
            "monto_reserva": tk.StringVar(),
            "estado": tk.StringVar(value="ACTIVA"),
            "observaciones": tk.StringVar(),
        }

        self._build_ui()
        self._load_propiedades_cache()
        self._load_data()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Tabla
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        cols = ("tipo", "prop", "cliente", "fecha", "monto", "estado")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse", height=18)
        headers = {
            "tipo": "Tipo",
            "prop": "Propiedad",
            "cliente": "Cliente",
            "fecha": "Fecha",
            "monto": "Monto",
            "estado": "Estado",
        }
        widths = {"tipo": 100, "prop": 200, "cliente": 160, "fecha": 110, "monto": 110, "estado": 110}
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Formulario
        form = ttk.LabelFrame(self, text="Datos de la Reserva", padding=10)
        form.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ttk.Label(form, text="Tipo:").grid(row=0, column=0, sticky="e", pady=3)
        cb_tipo = ttk.Combobox(
            form,
            textvariable=self.vars["tipo_propiedad"],
            values=["TERRENO", "EDIFICACION"],
            state="readonly",
            width=24,
        )
        cb_tipo.grid(row=0, column=1, sticky="w")
        cb_tipo.bind("<<ComboboxSelected>>", lambda e: self._load_propiedades_cache())

        ttk.Label(form, text="Propiedad:").grid(row=1, column=0, sticky="e", pady=3)
        self.cb_prop = ttk.Combobox(
            form,
            textvariable=self.vars["propiedad_id"],
            values=[],
            state="readonly",
            width=36,
        )
        self.cb_prop.grid(row=1, column=1, sticky="w")

        ttk.Label(form, text="Cliente:").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["cliente"], width=32).grid(row=2, column=1, sticky="w")

        ttk.Label(form, text="Fecha (YYYY-MM-DD):").grid(row=3, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["fecha_reserva"], width=18).grid(row=3, column=1, sticky="w")

        ttk.Label(form, text="Monto:").grid(row=4, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["monto_reserva"], width=18).grid(row=4, column=1, sticky="w")

        ttk.Label(form, text="Estado:").grid(row=5, column=0, sticky="e", pady=3)
        ttk.Combobox(
            form,
            textvariable=self.vars["estado"],
            values=["ACTIVA", "CANCELADA", "CONFIRMADA"],
            state="readonly",
            width=24,
        ).grid(row=5, column=1, sticky="w")

        ttk.Label(form, text="Observaciones:").grid(row=6, column=0, sticky="ne", pady=3)
        ttk.Entry(form, textvariable=self.vars["observaciones"], width=32).grid(row=6, column=1, sticky="we")

        # Botonera
        btns = ttk.Frame(form)
        btns.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="Nuevo", command=self._nuevo).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Guardar", command=self._guardar).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Confirmar", command=self._confirmar).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="Cancelar", command=self._cancelar).grid(row=0, column=3, padx=4)
        ttk.Button(btns, text="Eliminar", command=self._eliminar).grid(row=0, column=4, padx=4)
        ttk.Button(btns, text="Volver", command=self._volver).grid(row=0, column=5, padx=4)

    # ------------- Data helpers -------------
    def _load_propiedades_cache(self) -> None:
        """Carga el combo de propiedades según tipo seleccionado."""
        tipo = self.vars["tipo_propiedad"].get()
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
        self.vars["propiedad_id"].set("")

    def _label_to_id(self, label: str) -> Optional[int]:
        try:
            return int(label.split("|", 1)[0].strip()) if label else None
        except Exception:
            return None

    def _load_data(self) -> None:
        for r in self.tree.get_children():
            self.tree.delete(r)
        for r in self.rsvc.listar():
            prop_txt = f"{r.tipo_propiedad} #{r.propiedad_id}"
            self.tree.insert(
                "",
                "end",
                iid=r.id,
                values=(r.tipo_propiedad, prop_txt, r.cliente, r.fecha_reserva, r.monto_reserva, r.estado),
            )

    def _on_select(self, _e=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        r = self.rsvc.obtener(rid)
        if not r:
            return
        self.selected_id = r.id
        self.vars["tipo_propiedad"].set(r.tipo_propiedad)
        self._load_propiedades_cache()
        # set propiedad coincidente
        for _, lab in self._cache_prop:
            if self._label_to_id(lab) == r.propiedad_id:
                self.vars["propiedad_id"].set(lab)
                break
        self.vars["cliente"].set(r.cliente)
        self.vars["fecha_reserva"].set(r.fecha_reserva)
        self.vars["monto_reserva"].set(str(r.monto_reserva))
        self.vars["estado"].set(r.estado)
        self.vars["observaciones"].set(r.observaciones or "")

    # ------------- Acciones -------------
    def _nuevo(self) -> None:
        self.selected_id = None
        for k, v in self.vars.items():
            v.set("")
        self.vars["tipo_propiedad"].set("TERRENO")
        self.vars["estado"].set("ACTIVA")
        self._load_propiedades_cache()

    def _collect_form(self) -> dict:
        tipo = self.vars["tipo_propiedad"].get()
        prop_id = self._label_to_id(self.vars["propiedad_id"].get())
        if not prop_id:
            raise ValueError("Debe seleccionar una propiedad.")
        monto_str = self.vars["monto_reserva"].get().replace(",", ".").strip()
        try:
            monto = float(monto_str) if monto_str else 0.0
        except ValueError:
            raise ValueError("El monto de reserva es inválido.")
        if monto <= 0:
            raise ValueError("El monto de reserva debe ser positivo.")
        datos = {
            "tipo_propiedad": tipo,
            "propiedad_id": int(prop_id),
            "cliente": self.vars["cliente"].get().strip(),
            "fecha_reserva": self.vars["fecha_reserva"].get().strip(),
            "monto_reserva": monto,
            "estado": self.vars["estado"].get(),
            "observaciones": self.vars["observaciones"].get().strip() or None,
        }
        return datos

    def _guardar(self) -> None:
        try:
            datos = self._collect_form()
            if self.selected_id:
                self.rsvc.actualizar(self.selected_id, datos)
            else:
                self.selected_id = self.rsvc.crear(datos)
            self._load_data()
            messagebox.showinfo("Éxito", "Reserva guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _confirmar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return
        try:
            self.rsvc.confirmar(self.selected_id)
            self._load_data()
            self.vars["estado"].set("CONFIRMADA")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _cancelar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return
        try:
            self.rsvc.cancelar(self.selected_id)
            self._load_data()
            self.vars["estado"].set("CANCELADA")
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
            self._load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self) -> None:
        if hasattr(self.app, "go_back"):
            self.app.go_back()
        elif hasattr(self.app, "show_dashboard"):
            self.app.show_dashboard()
        else:
            pass

