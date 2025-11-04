# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from services.edificacion_service import EdificacionService
from services.terreno_service import TerrenoService
from entities.edificacion import Edificacion


class EdificacionesScreen(tk.Frame):
    """
    ABM de Edificaciones con selector múltiple de Terrenos.
    Permite crear, editar, eliminar y cambiar estado de edificaciones,
    vinculándolas a uno o más terrenos mediante dos Listbox (Disponibles/Seleccionados).
    """

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.esvc = EdificacionService()
        self.tsvc = TerrenoService()
        self.selected_id = None

        # cache de terrenos: id -> etiqueta
        self._terrenos_all: dict[int, str] = {}

        self._build_ui()
        self._load_terrenos_cache()
        self._load_data()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # ===== Tabla (izquierda)
        frame_table = ttk.Frame(self)
        frame_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        cols = ("tipo", "sup", "amb", "hab", "ban", "coch", "pat", "pil", "estado", "terr")
        self.tree = ttk.Treeview(
            frame_table,
            columns=cols,
            show="headings",
            selectmode="browse",
            height=18
        )
        headers = {
            "tipo": "Tipo",
            "sup": "Sup. cub. (m²)",
            "amb": "Amb",
            "hab": "Hab",
            "ban": "Baños",
            "coch": "Coch",
            "pat": "Patio",
            "pil": "Pileta",
            "estado": "Estado",
            "terr": "Terrenos",
        }
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=110 if c in ("tipo","estado","terr") else 90, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ===== Formulario (derecha)
        form = ttk.LabelFrame(self, text="Datos de la Edificación", padding=10)
        form.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        for i in range(0, 12):
            form.rowconfigure(i, weight=0)
        form.columnconfigure(0, weight=0)
        form.columnconfigure(1, weight=1)

        self.vars = {
            "nombre": tk.StringVar(),
            "tipo": tk.StringVar(value="CASA"),
            "superficie_cubierta": tk.StringVar(),
            "ambientes": tk.StringVar(),
            "habitaciones": tk.StringVar(),
            "banios": tk.StringVar(),
            "cochera": tk.BooleanVar(value=False),
            "patio": tk.BooleanVar(value=False),
            "pileta": tk.BooleanVar(value=False),
            "estado": tk.StringVar(value="DISPONIBLE"),
            "observaciones": tk.StringVar(),
        }

        # fila 0
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["nombre"], width=28).grid(row=0, column=1, sticky="we")

        # fila 1
        ttk.Label(form, text="Tipo:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Combobox(form, textvariable=self.vars["tipo"],
                     values=["CASA","DUPLEX","DEPARTAMENTO","LOCAL","GALPON"],
                     state="readonly", width=25).grid(row=1, column=1, sticky="w")

        # fila 2 a 4
        ttk.Label(form, text="Sup. cub. (m²):").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["superficie_cubierta"], width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(form, text="Ambientes:").grid(row=3, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["ambientes"], width=10).grid(row=3, column=1, sticky="w")

        ttk.Label(form, text="Habitaciones:").grid(row=4, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["habitaciones"], width=10).grid(row=4, column=1, sticky="w")

        # fila 5
        ttk.Label(form, text="Baños:").grid(row=5, column=0, sticky="e", pady=3)
        ttk.Entry(form, textvariable=self.vars["banios"], width=10).grid(row=5, column=1, sticky="w")

        # fila 6: checks
        checks = ttk.Frame(form)
        checks.grid(row=6, column=0, columnspan=2, sticky="w", pady=3)
        ttk.Checkbutton(checks, text="Cochera", variable=self.vars["cochera"]).grid(row=0, column=0, padx=(0,8))
        ttk.Checkbutton(checks, text="Patio", variable=self.vars["patio"]).grid(row=0, column=1, padx=(0,8))
        ttk.Checkbutton(checks, text="Pileta", variable=self.vars["pileta"]).grid(row=0, column=2)

        # fila 7: estado
        ttk.Label(form, text="Estado:").grid(row=7, column=0, sticky="e", pady=3)
        ttk.Combobox(form, textvariable=self.vars["estado"],
                     values=["DISPONIBLE","RESERVADO","VENDIDO"],
                     state="readonly", width=25).grid(row=7, column=1, sticky="w")

        # fila 8: observaciones
        ttk.Label(form, text="Observaciones:").grid(row=8, column=0, sticky="ne", pady=3)
        ttk.Entry(form, textvariable=self.vars["observaciones"], width=28).grid(row=8, column=1, sticky="we")

        # ===== Selector múltiple Terrenos (fila 9..)
        box = ttk.LabelFrame(form, text="Terrenos asociados", padding=6)
        box.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=(8,4))
        box.columnconfigure(0, weight=1)
        box.columnconfigure(1, weight=0)
        box.columnconfigure(2, weight=1)
        box.rowconfigure(1, weight=1)

        ttk.Label(box, text="Disponibles").grid(row=0, column=0)
        ttk.Label(box, text="Seleccionados").grid(row=0, column=2)

        self.lb_disp = tk.Listbox(box, selectmode="extended", height=8, exportselection=False)
        self.lb_sel  = tk.Listbox(box, selectmode="extended", height=8, exportselection=False)
        self.lb_disp.grid(row=1, column=0, sticky="nsew", padx=(0,6))
        self.lb_sel.grid(row=1, column=2, sticky="nsew", padx=(6,0))

        mid = ttk.Frame(box)
        mid.grid(row=1, column=1, sticky="ns")
        ttk.Button(mid, text="→", width=3, command=self._add_selected).grid(row=0, column=0, pady=2)
        ttk.Button(mid, text="←", width=3, command=self._remove_selected).grid(row=1, column=0, pady=2)

        # ===== Botones finales
        btns = ttk.Frame(form)
        btns.grid(row=10, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Nuevo", command=self._nuevo).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Guardar", command=self._guardar).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Eliminar", command=self._eliminar).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="Volver", command=self._volver).grid(row=0, column=3, padx=4)

    # ---------------- Data helpers ----------------
    def _load_terrenos_cache(self):
        self._terrenos_all.clear()
        for t in self.tsvc.listar():
            self._terrenos_all[int(t.id)] = f"ID {t.id} · Mz {t.manzana} · Lote {t.numero_lote} · {t.superficie} m²"

    def _refresh_terrenos_lists(self, selected_ids: List[int] | None):
        selected = set(selected_ids or [])
        self.lb_disp.delete(0, tk.END)
        self.lb_sel.delete(0, tk.END)
        for tid, label in sorted(self._terrenos_all.items()):
            if tid in selected:
                self.lb_sel.insert(tk.END, f"{tid} | {label}")
            else:
                self.lb_disp.insert(tk.END, f"{tid} | {label}")

    def _parse_listbox_ids(self, lb: tk.Listbox) -> List[int]:
        ids = []
        for i in range(lb.size()):
            item = lb.get(i)
            tid = int(item.split("|", 1)[0].strip())
            ids.append(tid)
        return ids

    def _selected_ids_from_listbox(self, lb: tk.Listbox) -> List[int]:
        ids = []
        for i in lb.curselection():
            item = lb.get(i)
            tid = int(item.split("|", 1)[0].strip())
            ids.append(tid)
        return ids

    # ---------------- Load/list ----------------
    def _load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for e in self.esvc.listar():
            terrs = ",".join(str(t) for t in (e.terrenos_ids or []))
            self.tree.insert(
                "", "end", iid=e.id,
                values=(
                    e.tipo,
                    e.superficie_cubierta or "",
                    e.ambientes or "",
                    e.habitaciones or "",
                    e.banios or "",
                    "Sí" if e.cochera else "No",
                    "Sí" if e.patio else "No",
                    "Sí" if e.pileta else "No",
                    e.estado,
                    terrs
                )
            )

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        eid = int(sel[0])
        e = self.esvc.obtener(eid)
        if not e:
            return
        self.selected_id = e.id
        # Set vars
        self.vars["nombre"].set(e.nombre or "")
        self.vars["tipo"].set(e.tipo)
        self.vars["superficie_cubierta"].set("" if e.superficie_cubierta is None else str(e.superficie_cubierta))
        self.vars["ambientes"].set("" if e.ambientes is None else str(e.ambientes))
        self.vars["habitaciones"].set("" if e.habitaciones is None else str(e.habitaciones))
        self.vars["banios"].set("" if e.banios is None else str(e.banios))
        self.vars["cochera"].set(bool(e.cochera))
        self.vars["patio"].set(bool(e.patio))
        self.vars["pileta"].set(bool(e.pileta))
        self.vars["estado"].set(e.estado)
        self.vars["observaciones"].set(e.observaciones or "")
        self._refresh_terrenos_lists(e.terrenos_ids)

    # ---------------- Actions ----------------
    def _nuevo(self):
        self.selected_id = None
        for k, v in self.vars.items():
            if isinstance(v, tk.BooleanVar):
                v.set(False)
            elif isinstance(v, tk.StringVar):
                v.set("")
        self.vars["tipo"].set("CASA")
        self.vars["estado"].set("DISPONIBLE")
        self._load_terrenos_cache()
        self._refresh_terrenos_lists([])

    def _collect_form(self) -> dict:
        def to_float(s): 
            return None if not s.strip() else float(s.replace(",", "."))
        def to_int(s):
            return None if not s.strip() else int(s)

        datos = {
            "nombre": self.vars["nombre"].get().strip() or None,
            "tipo": self.vars["tipo"].get(),
            "superficie_cubierta": to_float(self.vars["superficie_cubierta"].get()),
            "ambientes": to_int(self.vars["ambientes"].get()),
            "habitaciones": to_int(self.vars["habitaciones"].get()),
            "banios": to_int(self.vars["banios"].get()),
            "cochera": bool(self.vars["cochera"].get()),
            "patio": bool(self.vars["patio"].get()),
            "pileta": bool(self.vars["pileta"].get()),
            "estado": self.vars["estado"].get(),
            "observaciones": self.vars["observaciones"].get().strip() or None,
            "terrenos_ids": self._parse_listbox_ids(self.lb_sel),
        }
        return datos

    def _guardar(self):
        try:
            datos = self._collect_form()
            if self.selected_id:
                self.esvc.actualizar(self.selected_id, datos)
            else:
                self.selected_id = self.esvc.crear(datos)
            self._load_data()
            messagebox.showinfo("Éxito", "Edificación guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self):
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una edificación.")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la edificación seleccionada?"):
            return
        try:
            self.esvc.eliminar(self.selected_id)
            self.selected_id = None
            self._nuevo()
            self._load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _volver(self):
        if hasattr(self.app, "go_back"):
            self.app.go_back()
        elif hasattr(self.app, "show_dashboard"):
            self.app.show_dashboard()
        else:
            # fallback: nada
            pass

    # ---- mover entre listboxes ----
    def _add_selected(self):
        ids = self._selected_ids_from_listbox(self.lb_disp)
        # mover a seleccionados
        all_sel = self._parse_listbox_ids(self.lb_sel)
        for tid in ids:
            if tid not in all_sel:
                self.lb_sel.insert(tk.END, f"{tid} | {self._terrenos_all.get(tid,'')}")
        # quitar de disponibles (reconstruimos ambas listas para simplicidad)
        self._refresh_terrenos_lists(self._parse_listbox_ids(self.lb_sel))

    def _remove_selected(self):
        ids = self._selected_ids_from_listbox(self.lb_sel)
        remaining = [tid for tid in self._parse_listbox_ids(self.lb_sel) if tid not in ids]
        self._refresh_terrenos_lists(remaining)

