# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from entities.terreno import Terreno
from services.terreno_service import TerrenoService


class TerrenosScreen(tk.Frame):
    """
    Pantalla ABM de terrenos.
    Permite listar, crear, editar y eliminar terrenos.
    """

    def __init__(self, parent: tk.Misc, app: Optional[object] = None) -> None:
        super().__init__(parent)
        self.app = app
        self.service = TerrenoService()
        self.selected_id: Optional[int] = None

        self._build_ui()
        self._load_data()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # ---- Tabla de terrenos ----
        frame_table = ttk.Frame(self)
        frame_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tree = ttk.Treeview(
            frame_table,
            columns=("manzana", "numero_lote", "superficie", "estado"),
            show="headings",
            selectmode="browse",
            height=15,
        )
        self.tree.heading("manzana", text="Manzana")
        self.tree.heading("numero_lote", text="Lote")
        self.tree.heading("superficie", text="Superficie (m²)")
        self.tree.heading("estado", text="Estado")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ---- Formulario lateral ----
        frame_form = ttk.LabelFrame(self, text="Datos del Terreno", padding=10)
        frame_form.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.vars: dict[str, tk.StringVar] = {
            "manzana": tk.StringVar(),
            "numero_lote": tk.StringVar(),
            "superficie": tk.StringVar(),
            "ubicacion": tk.StringVar(),
            "nomenclatura": tk.StringVar(),
            "estado": tk.StringVar(value="DISPONIBLE"),
            "observaciones": tk.StringVar(),
        }

        labels = [
            ("Manzana:", "manzana"),
            ("Lote:", "numero_lote"),
            ("Superficie (m²):", "superficie"),
            ("Ubicación:", "ubicacion"),
            ("Nomenclatura:", "nomenclatura"),
            ("Estado:", "estado"),
            ("Observaciones:", "observaciones"),
        ]

        for i, (lbl, key) in enumerate(labels):
            ttk.Label(frame_form, text=lbl).grid(row=i, column=0, sticky="e", pady=3)
            if key == "estado":
                cb = ttk.Combobox(
                    frame_form,
                    textvariable=self.vars[key],
                    values=["DISPONIBLE", "RESERVADO", "VENDIDO"],
                    state="readonly",
                    width=18,
                )
                cb.grid(row=i, column=1, sticky="w")
            else:
                ttk.Entry(frame_form, textvariable=self.vars[key], width=30).grid(
                    row=i, column=1, pady=3, sticky="w"
                )

        # ---- Botones ----
        frame_btns = ttk.Frame(frame_form)
        frame_btns.grid(row=len(labels), column=0, columnspan=2, pady=10)

        ttk.Button(frame_btns, text="Nuevo", command=self._nuevo).grid(row=0, column=0, padx=5)
        ttk.Button(frame_btns, text="Guardar", command=self._guardar).grid(row=0, column=1, padx=5)
        ttk.Button(frame_btns, text="Eliminar", command=self._eliminar).grid(row=0, column=2, padx=5)
        ttk.Button(frame_btns, text="Volver", command=self._volver).grid(row=0, column=3, padx=5)

    # ---------------- Datos ----------------
    def _load_data(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        terrenos = self.service.listar()
        for t in terrenos:
            self.tree.insert("", "end", iid=t.id, values=(t.manzana, t.numero_lote, t.superficie, t.estado))

    def _on_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        tid = int(sel[0])
        t = self.service.obtener(tid)
        if not t:
            return
        self.selected_id = t.id
        # map fields to vars; ensure strings
        self.vars["manzana"].set(t.manzana or "")
        self.vars["numero_lote"].set(t.numero_lote or "")
        self.vars["superficie"].set(str(t.superficie) if t.superficie is not None else "")
        self.vars["ubicacion"].set(t.ubicacion or "")
        self.vars["nomenclatura"].set(t.nomenclatura or "")
        self.vars["estado"].set(t.estado or "DISPONIBLE")
        self.vars["observaciones"].set(t.observaciones or "")

    # ---------------- Acciones ----------------
    def _nuevo(self) -> None:
        self.selected_id = None
        for v in self.vars.values():
            v.set("")
        self.vars["estado"].set("DISPONIBLE")

    def _guardar(self) -> None:
        datos = {k: v.get().strip() for k, v in self.vars.items()}
        # convertir superficie a float si se provee
        try:
            datos["superficie"] = float(datos.get("superficie") or 0)
        except ValueError:
            messagebox.showerror("Error", "La superficie debe ser un número válido.")
            return
        try:
            if self.selected_id:
                self.service.actualizar(self.selected_id, datos)
            else:
                self.service.crear(datos)
            self._load_data()
            self._nuevo()
            messagebox.showinfo("Éxito", "Terreno guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione un terreno.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el terreno seleccionado?"):
            return
        try:
            self.service.eliminar(self.selected_id)
            self._load_data()
            self._nuevo()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self) -> None:
        """Regresa al dashboard o pantalla anterior."""
        if hasattr(self.app, "go_back"):
            self.app.go_back()  # type: ignore[attr-defined]
        elif hasattr(self.app, "show_dashboard"):
            self.app.show_dashboard()  # type: ignore[attr-defined]
        elif hasattr(self.app, "show_screen"):
            try:
                from view.dashboard_screen import DashboardScreen

                self.app.show_screen(DashboardScreen)  # type: ignore[attr-defined]
            except Exception:
                pass

