# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

from services.loteo_service import LoteoService
from services.terreno_service import TerrenoService


class LoteosScreen(tk.Frame):
    """ABM de Loteos con doble Listbox para asignar Terrenos."""

    def __init__(self, parent: tk.Misc, app: Optional[object] = None) -> None:
        super().__init__(parent)
        self.app = app
        self.lsvc = LoteoService()
        self.tsvc = TerrenoService()
        self.selected_id: Optional[int] = None

        # cache de terrenos: id -> etiqueta
        self._terrenos_all: dict[int, str] = {}

        self._build_ui()
        self._load_terrenos_cache()
        self._load_data()

    # --------------- UI ---------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # Tabla izquierda
        frame_table = ttk.Frame(self)
        frame_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        cols = ("nombre", "ubicacion", "municipio", "provincia", "estado", "terr")
        self.tree = ttk.Treeview(
            frame_table,
            columns=cols,
            show="headings",
            selectmode="browse",
            height=18,
        )
        headers = {
            "nombre": "Nombre",
            "ubicacion": "Ubicación",
            "municipio": "Municipio",
            "provincia": "Provincia",
            "estado": "Estado",
            "terr": "Terrenos",
        }
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=120 if c in ("nombre", "estado", "terr") else 110, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Formulario derecha
        form = ttk.LabelFrame(self, text="Datos del Loteo", padding=10)
        form.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        for i in range(0, 14):
            form.rowconfigure(i, weight=0)
        form.columnconfigure(0, weight=0)
        form.columnconfigure(1, weight=1)

        self.vars: dict[str, tk.Variable] = {
            "nombre": tk.StringVar(),
            "ubicacion": tk.StringVar(),
            "municipio": tk.StringVar(),
            "provincia": tk.StringVar(),
            "fecha_inicio": tk.StringVar(),
            "fecha_fin": tk.StringVar(),
            "estado": tk.StringVar(value="ACTIVO"),
            "observaciones": tk.StringVar(),
        }

        # filas
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["nombre"], width=28).grid(row=0, column=1, sticky="we")

        ttk.Label(form, text="Ubicación:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["ubicacion"], width=28).grid(row=1, column=1, sticky="we")

        ttk.Label(form, text="Municipio:").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["municipio"], width=28).grid(row=2, column=1, sticky="we")

        ttk.Label(form, text="Provincia:").grid(row=3, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["provincia"], width=28).grid(row=3, column=1, sticky="we")

        ttk.Label(form, text="F. inicio (yyyy-mm-dd):").grid(row=4, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["fecha_inicio"], width=28).grid(row=4, column=1, sticky="we")

        ttk.Label(form, text="F. fin (yyyy-mm-dd):").grid(row=5, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["fecha_fin"], width=28).grid(row=5, column=1, sticky="we")

        ttk.Label(form, text="Estado:").grid(row=6, column=0, sticky="e", pady=3)
        ttk.Combobox(
            form,
            textvariable=self.vars["estado"],
            values=["ACTIVO", "PAUSADO", "CERRADO"],
            state="readonly",
            width=25,
        ).grid(row=6, column=1, sticky="w")

        ttk.Label(form, text="Observaciones:").grid(row=7, column=0, sticky="ne", pady=3)
        ttk.Entry(form, textvariable=self.vars["observaciones"], width=28).grid(row=7, column=1, sticky="we")

        # Selector múltiple de Terrenos
        box = ttk.LabelFrame(form, text="Terrenos asociados", padding=6)
        box.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(8, 4))
        box.columnconfigure(0, weight=1)
        box.columnconfigure(1, weight=0)
        box.columnconfigure(2, weight=1)
        box.rowconfigure(1, weight=1)

        ttk.Label(box, text="Disponibles").grid(row=0, column=0)
        ttk.Label(box, text="Asignados").grid(row=0, column=2)

        self.lb_disp = tk.Listbox(box, selectmode="extended", height=8, exportselection=False)
        self.lb_sel = tk.Listbox(box, selectmode="extended", height=8, exportselection=False)
        self.lb_disp.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.lb_sel.grid(row=1, column=2, sticky="nsew", padx=(6, 0))

        mid = ttk.Frame(box)
        mid.grid(row=1, column=1, sticky="ns")
        ttk.Button(mid, text=">>", width=3, command=self._add_selected).grid(row=0, column=0, pady=2)
        ttk.Button(mid, text="<<", width=3, command=self._remove_selected).grid(row=1, column=0, pady=2)

        # Botones finales
        btns = ttk.Frame(form)
        btns.grid(row=9, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btns, text="Nuevo", command=self._nuevo).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Guardar", command=self._guardar).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Eliminar", command=self._eliminar).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="Volver", command=self._volver).grid(row=0, column=3, padx=4)

    # --------------- Helpers de datos ---------------
    def _load_terrenos_cache(self) -> None:
        self._terrenos_all.clear()
        for t in self.tsvc.listar():
            label = f"ID {t.id} · Mz {t.manzana} · Lote {t.numero_lote} · {t.superficie} m2"
            self._terrenos_all[int(t.id)] = label

    def _refresh_terrenos_lists(self, selected_ids: List[int] | None) -> None:
        selected = set(selected_ids or [])
        self.lb_disp.delete(0, tk.END)
        self.lb_sel.delete(0, tk.END)
        for tid, label in sorted(self._terrenos_all.items()):
            if tid in selected:
                self.lb_sel.insert(tk.END, f"{tid} | {label}")
            else:
                self.lb_disp.insert(tk.END, f"{tid} | {label}")

    def _parse_listbox_ids(self, lb: tk.Listbox) -> List[int]:
        ids: List[int] = []
        for i in range(lb.size()):
            item = lb.get(i)
            tid = int(item.split("|", 1)[0].strip())
            ids.append(tid)
        return ids

    def _selected_ids_from_listbox(self, lb: tk.Listbox) -> List[int]:
        ids: List[int] = []
        for i in lb.curselection():
            item = lb.get(i)
            tid = int(item.split("|", 1)[0].strip())
            ids.append(tid)
        return ids

    # --------------- Carga/Lista ---------------
    def _load_data(self) -> None:
        for r in self.tree.get_children():
            self.tree.delete(r)
        for l in self.lsvc.listar():
            terrs = ",".join(str(t) for t in (l.terrenos_ids or []))
            self.tree.insert(
                "",
                "end",
                iid=l.id,
                values=(
                    l.nombre,
                    l.ubicacion or "",
                    l.municipio or "",
                    l.provincia or "",
                    l.estado or "ACTIVO",
                    terrs,
                ),
            )

    def _on_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        lid = int(sel[0])
        l = self.lsvc.obtener(lid)
        if not l:
            return
        self.selected_id = l.id
        # map fields
        self.vars["nombre"].set(l.nombre or "")
        self.vars["ubicacion"].set(l.ubicacion or "")
        self.vars["municipio"].set(l.municipio or "")
        self.vars["provincia"].set(l.provincia or "")
        self.vars["fecha_inicio"].set(l.fecha_inicio or "")
        self.vars["fecha_fin"].set(l.fecha_fin or "")
        self.vars["estado"].set(l.estado or "ACTIVO")
        self.vars["observaciones"].set(l.observaciones or "")
        self._refresh_terrenos_lists(l.terrenos_ids)

    # --------------- Acciones ---------------
    def _nuevo(self) -> None:
        self.selected_id = None
        for k, v in self.vars.items():
            if isinstance(v, tk.StringVar):
                v.set("")
        self.vars["estado"].set("ACTIVO")
        self._refresh_terrenos_lists([])

    def _guardar(self) -> None:
        datos = {
            "nombre": self.vars["nombre"].get().strip(),
            "ubicacion": (self.vars["ubicacion"].get().strip() or None),
            "municipio": (self.vars["municipio"].get().strip() or None),
            "provincia": (self.vars["provincia"].get().strip() or None),
            "fecha_inicio": (self.vars["fecha_inicio"].get().strip() or None),
            "fecha_fin": (self.vars["fecha_fin"].get().strip() or None),
            "estado": self.vars["estado"].get().strip() or "ACTIVO",
            "observaciones": (self.vars["observaciones"].get().strip() or None),
            "terrenos_ids": self._parse_listbox_ids(self.lb_sel),
        }
        try:
            if self.selected_id:
                self.lsvc.actualizar(self.selected_id, datos)
            else:
                new_id = self.lsvc.crear(datos)
                self.selected_id = new_id
            self._load_data()
            messagebox.showinfo("Éxito", "Loteo guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self) -> None:
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione un loteo.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el loteo seleccionado?"):
            return
        try:
            self.lsvc.eliminar(self.selected_id)
            self._load_data()
            self._nuevo()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self) -> None:
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

    # --------------- Listbox actions ---------------
    def _add_selected(self) -> None:
        for i in list(self.lb_disp.curselection()):
            item = self.lb_disp.get(i)
            self.lb_sel.insert(tk.END, item)
        # remove from left after adding
        for i in reversed(self.lb_disp.curselection()):
            self.lb_disp.delete(i)

    def _remove_selected(self) -> None:
        for i in list(self.lb_sel.curselection()):
            item = self.lb_sel.get(i)
            self.lb_disp.insert(tk.END, item)
        for i in reversed(self.lb_sel.curselection()):
            self.lb_sel.delete(i)

