# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

SortFunc = Callable[[Any], Any]


class BaseTable(ttk.Frame):
    """
    Tabla base sobre ttk.Treeview con:
    - Definición declarativa de columnas
    - Ordenamiento por columna (toggle asc/desc)
    - Carga eficiente de filas
    - Selección de una o varias filas
    """

    def __init__(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, str, int]],  # (id_col, header, width)
        multiselect: bool = False,
        height: int = 15,
        on_select: Optional[Callable[[List[str]], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._columns = columns
        self._on_select = on_select
        self._sort_state: Dict[str, bool] = {}  # col_id -> asc(True)/desc(False)

        # Treeview
        selectmode = "extended" if multiselect else "browse"
        self.tree = ttk.Treeview(
            self,
            columns=[c[0] for c in columns],
            show="headings",
            selectmode=selectmode,
            height=height,
        )
        self.tree.pack(fill="both", expand=True)

        # Scrollbars
        vs = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

        vs.pack(side="right", fill="y")
        hs.pack(side="bottom", fill="x")

        # Configurar columnas
        for col_id, header, width in columns:
            self.tree.heading(col_id, text=header, command=lambda c=col_id: self._toggle_sort(c))
            self.tree.column(col_id, width=width, stretch=True)

        # Bind selección
        self.tree.bind("<<TreeviewSelect>>", self._emit_selection)

        # Data cache para sort
        self._rows_cache: List[Tuple[str, List[Any]]] = []  # (iid, values)

    # ---------- API ----------
    def clear(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._rows_cache = []

    def load_rows(self, rows: Iterable[Tuple[str, List[Any]]]) -> None:
        """
        Carga filas. Cada fila: (iid, [values...]) donde values se alinean con self._columns.
        """
        self.clear()
        for iid, values in rows:
            self.tree.insert("", "end", iid=iid, values=values)
            self._rows_cache.append((iid, values))

    def add_row(self, iid: str, values: List[Any]) -> None:
        self.tree.insert("", "end", iid=iid, values=values)
        self._rows_cache.append((iid, values))

    def selected_ids(self) -> List[str]:
        return list(self.tree.selection())

    def selected_first_id(self) -> Optional[str]:
        sel = self.selected_ids()
        return sel[0] if sel else None

    # ---------- Sort ----------
    def _toggle_sort(self, col_id: str) -> None:
        asc = not self._sort_state.get(col_id, True)
        self._sort_state[col_id] = asc
        self._sort_by_column(col_id, asc)

    def _sort_by_column(self, col_id: str, asc: bool) -> None:
        # determinar índice de la columna
        col_index = [c[0] for c in self._columns].index(col_id)

        def cast(val: Any) -> Any:
            # intentar convertir a float/int para orden natural
            if isinstance(val, (int, float)):
                return val
            try:
                return float(str(val).replace(",", "."))
            except Exception:
                return str(val).lower()

        sorted_rows = sorted(self._rows_cache, key=lambda r: cast(r[1][col_index]), reverse=not asc)

        # repintar
        cache = sorted_rows[:]  # preserve order for rebuilding
        self.clear()
        for iid, values in cache:
            self.tree.insert("", "end", iid=iid, values=values)
            self._rows_cache.append((iid, values))

    # ---------- Internos ----------
    def _emit_selection(self, _evt=None) -> None:
        if self._on_select:
            self._on_select(self.selected_ids())

