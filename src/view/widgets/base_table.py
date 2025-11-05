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
        self._sort_state: Dict[str, bool] = {}  # legacy; not used in new visual sort
        self._headers: Dict[str, str] = {c[0]: c[1] for c in columns}
        self._sort_col: Optional[str] = None
        self._sort_desc: bool = False
        self._all_rows: List[Tuple[str, List[Any]]] = []
        self._filtered_rows: List[Tuple[str, List[Any]]] = []

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
            self.tree.heading(col_id, text=header, command=lambda c=col_id: self._on_column_click(c))
            self.tree.column(col_id, width=width, stretch=True)

        # Bind selección
        self.tree.bind("<<TreeviewSelect>>", self._emit_selection)

        # Legacy cache (not used by new API); kept for compatibility
        self._rows_cache: List[Tuple[str, List[Any]]] = []  # (iid, values)

    # ---------- API ----------
    def clear(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._rows_cache = []

    def load_rows(self, rows: Iterable[Tuple[str, List[Any]]]) -> None:
        """Carga filas y guarda el dataset original para búsquedas/ordenamientos."""
        data = list(rows or [])
        self._all_rows = data
        self._filtered_rows = list(self._all_rows)
        self._sort_col = None
        self._sort_desc = False
        self._refresh_tree()

    def add_row(self, iid: str, values: List[Any]) -> None:
        self.tree.insert("", "end", iid=iid, values=values)
        self._rows_cache.append((iid, values))

    def selected_ids(self) -> List[str]:
        return list(self.tree.selection())

    def selected_first_id(self) -> Optional[str]:
        sel = self.selected_ids()
        return sel[0] if sel else None

    # ---------- Sort ----------
    def _col_index(self, col_id: str) -> int:
        return [c[0] for c in self._columns].index(col_id)

    def _refresh_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for iid, values in self._filtered_rows:
            self.tree.insert("", "end", iid=iid, values=values)

    def filter_rows(self, query: str) -> None:
        q = (query or "").strip().lower()
        if not q:
            self._filtered_rows = list(self._all_rows)
        else:
            self._filtered_rows = [
                r for r in self._all_rows if any(q in str(cell).lower() for cell in r[1])
            ]
        # keep current sort, if any
        if self._sort_col is not None:
            self._apply_sort(self._sort_col, self._sort_desc)
        self._refresh_tree()

    def _apply_sort(self, col_id: str, desc: bool) -> None:
        idx = self._col_index(col_id)
        self._filtered_rows.sort(key=lambda r: str(r[1][idx]).lower(), reverse=desc)

    def _on_column_click(self, col_id: str) -> None:
        if self._sort_col == col_id:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_col = col_id
            self._sort_desc = False
        self._apply_sort(col_id, self._sort_desc)
        self._refresh_tree()
        arrow = " ↓" if self._sort_desc else " ↑"
        for c in self.tree["columns"]:
            self.tree.heading(c, text=self._headers.get(c, c))
        self.tree.heading(col_id, text=self._headers.get(col_id, col_id) + arrow)

    # ---------- Internos ----------
    def _emit_selection(self, _evt=None) -> None:
        if self._on_select:
            self._on_select(self.selected_ids())
