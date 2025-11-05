# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, List

from core.frame_manager import BaseScreen
from view.widgets.base_table import BaseTable
from view.widgets.base_form import BaseForm
from services.edificacion_service import EdificacionService
from services.terreno_service import TerrenoService
from entities.edificacion import Edificacion


class EdificacionesScreen(BaseScreen):
    """
    ABM de Edificaciones aplicando el patrón BaseTable + BaseForm.
    Incluye selector múltiple de Terrenos asociados y campos completos de la entidad.
    """

    def __init__(self, parent, app: Any, *args: Any) -> None:
        super().__init__(parent)
        self.app = app
        self.svc = EdificacionService()
        self.tsvc = TerrenoService()
        self._selected_id: Optional[int] = None
        self._current_terrenos: List[int] = []
        self._terrenos_all: dict[int, str] = {}

        self._build_ui()
        self._load_terrenos_cache()
        self._load_table()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        # Barra de búsqueda
        top = ttk.Frame(self)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        ttk.Label(top, text="Buscar:").pack(side="left")
        self.var_buscar = tk.StringVar()
        entry_buscar = ttk.Entry(top, textvariable=self.var_buscar, width=30)
        entry_buscar.pack(side="left", padx=5)
        entry_buscar.bind("<KeyRelease>", lambda e: self.tbl.filter_rows(self.var_buscar.get()))

        # Tabla
        left = ttk.Frame(self)
        left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

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
        right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)

        self.form = BaseForm(right)
        self.form.grid(row=0, column=0, sticky="nsew")
        self.form.add_entry("nombre", "Nombre:")
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
        self.form.add_entry("ambientes", "Ambientes:")
        self.form.add_entry("habitaciones", "Habitaciones:")
        self.form.add_entry("banios", "Baños (n):")
        self.form.add_check("cochera", "Cochera")
        self.form.add_check("patio", "Patio")
        self.form.add_check("pileta", "Pileta")
        self.form.add_combobox("estado", "Estado:", ["DISPONIBLE", "RESERVADO", "VENDIDO"], readonly=True)
        self.form.add_entry("observaciones", "Observaciones:")

        # Selector múltiple de Terrenos (disponibles/seleccionados)
        terr_box = ttk.LabelFrame(right, text="Terrenos asociados", padding=6)
        terr_box.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        terr_box.columnconfigure(0, weight=1)
        terr_box.columnconfigure(1, weight=0)
        terr_box.columnconfigure(2, weight=1)

        self.list_disp = tk.Listbox(terr_box, selectmode=tk.EXTENDED, height=10)
        self.list_disp.grid(row=0, column=0, sticky="nsew")

        btns = ttk.Frame(terr_box)
        btns.grid(row=0, column=1, padx=6)
        ttk.Button(btns, text=">", width=3, command=self._move_to_selected).grid(row=0, column=0, pady=2)
        ttk.Button(btns, text=">>", width=3, command=self._move_all_to_selected).grid(row=1, column=0, pady=2)
        ttk.Button(btns, text="<", width=3, command=self._move_to_available).grid(row=2, column=0, pady=2)
        ttk.Button(btns, text="<<", width=3, command=self._move_all_to_available).grid(row=3, column=0, pady=2)

        self.list_sel = tk.Listbox(terr_box, selectmode=tk.EXTENDED, height=10)
        self.list_sel.grid(row=0, column=2, sticky="nsew")

        self.form.add_actions([
            ("Nuevo", self._nuevo),
            ("Guardar", self._guardar),
            ("Eliminar", self._eliminar),
            ("Volver", self._volver),
        ])
        # Atajos
        self.form.bind("<<FormCancel>>", lambda e: self._volver())
        self.form.bind("<<FormNew>>", lambda e: self._nuevo())
        self.form.bind("<<FormSave>>", lambda e: self._guardar())

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

    def _load_terrenos_cache(self) -> None:
        self._terrenos_all = {}
        try:
            for t in self.tsvc.listar():
                if t.id is None:
                    continue
                label = f"{t.id} | Mz {t.manzana} · Lote {t.numero_lote} · {t.superficie} m²"
                self._terrenos_all[int(t.id)] = label
        except Exception:
            self._terrenos_all = {}

    def _refresh_terrenos_lists(self) -> None:
        disp_ids = [tid for tid in self._terrenos_all.keys() if tid not in set(self._current_terrenos)]
        sel_ids = list(self._current_terrenos)

        self.list_disp.delete(0, tk.END)
        for tid in sorted(disp_ids):
            self.list_disp.insert(tk.END, self._terrenos_all[tid])

        self.list_sel.delete(0, tk.END)
        for tid in sorted(sel_ids):
            self.list_sel.insert(tk.END, self._terrenos_all.get(tid, str(tid)))

    def _labels_to_ids(self, items: List[str]) -> List[int]:
        ids: List[int] = []
        for lab in items:
            try:
                ids.append(int(lab.split("|", 1)[0].strip()))
            except Exception:
                continue
        return ids

    def _move_to_selected(self) -> None:
        items = [self.list_disp.get(i) for i in self.list_disp.curselection()]
        ids = self._labels_to_ids(items)
        for tid in ids:
            if tid not in self._current_terrenos:
                self._current_terrenos.append(tid)
        self._refresh_terrenos_lists()

    def _move_all_to_selected(self) -> None:
        self._current_terrenos = list(self._terrenos_all.keys())
        self._refresh_terrenos_lists()

    def _move_to_available(self) -> None:
        items = [self.list_sel.get(i) for i in self.list_sel.curselection()]
        ids = set(self._labels_to_ids(items))
        self._current_terrenos = [tid for tid in self._current_terrenos if tid not in ids]
        self._refresh_terrenos_lists()

    def _move_all_to_available(self) -> None:
        self._current_terrenos = []
        self._refresh_terrenos_lists()

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
        self.form.set_values(
            {
                "nombre": e.nombre or "",
                "tipo": e.tipo,
                "superficie_cubierta": e.superficie_cubierta if e.superficie_cubierta is not None else "",
                "ambientes": e.ambientes if e.ambientes is not None else "",
                "habitaciones": e.habitaciones if e.habitaciones is not None else "",
                "banios": e.banios if e.banios is not None else "",
                "cochera": bool(e.cochera),
                "patio": bool(e.patio),
                "pileta": bool(e.pileta),
                "estado": e.estado,
                "observaciones": e.observaciones or "",
            }
        )
        self._refresh_terrenos_lists()

    def _collect_form(self) -> dict:
        data = self.form.get_values()
        out: dict[str, Any] = {}
        # Campos básicos
        out["nombre"] = (str(data.get("nombre") or "").strip() or None)
        if data.get("tipo"):
            out["tipo"] = data.get("tipo")
        sc = (data.get("superficie_cubierta") or "").strip()
        if sc:
            out["superficie_cubierta"] = float(sc.replace(",", "."))
        else:
            out["superficie_cubierta"] = None
        # Enteros opcionales no negativos
        def to_int_opt(v: str) -> Optional[int]:
            s = (v or "").strip()
            if s == "":
                return None
            iv = int(s)
            if iv < 0:
                raise ValueError
            return iv
        try:
            out["ambientes"] = to_int_opt(str(data.get("ambientes") or ""))
            out["habitaciones"] = to_int_opt(str(data.get("habitaciones") or ""))
            out["banios"] = to_int_opt(str(data.get("banios") or ""))
        except Exception:
            raise ValueError("Los campos numéricos deben ser enteros no negativos.")
        # Booleanos
        out["cochera"] = bool(data.get("cochera"))
        out["patio"] = bool(data.get("patio"))
        out["pileta"] = bool(data.get("pileta"))
        # Estado y observaciones
        if data.get("estado"):
            out["estado"] = data.get("estado")
        out["observaciones"] = (str(data.get("observaciones") or "").strip() or None)
        # Terrenos seleccionados
        out["terrenos_ids"] = list(dict.fromkeys(int(t) for t in self._current_terrenos))
        return out

    # ---------------- Acciones ----------------
    def _nuevo(self) -> None:
        self._selected_id = None
        self._current_terrenos = []
        self.form.clear()
        self.form.set_values({"tipo": "CASA", "estado": "DISPONIBLE"})
        self._refresh_terrenos_lists()

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

