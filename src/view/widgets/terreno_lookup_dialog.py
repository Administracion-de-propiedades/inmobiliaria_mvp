from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from services.terreno_service import TerrenoService


class TerrenoLookupDialog:
    """Diálogo para buscar por nomenclatura y vincular/crear un Terreno."""

    def __init__(
        self,
        parent: tk.Misc,
        terreno_service: Optional[TerrenoService] = None,
        on_select: Optional[Callable[[int], None]] = None,
    ) -> None:
        self.parent = parent
        self.svc = terreno_service or TerrenoService()
        self.on_select = on_select

        self.top = tk.Toplevel(parent)
        self.top.title("Agregar datos del terreno")
        self.top.transient(parent.winfo_toplevel())
        self.top.grab_set()
        self.top.resizable(False, False)

        self._build_ui()

        self.top.bind("<Escape>", lambda _e: self._close())
        self.entry_nom.focus_set()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}
        main = ttk.Frame(self.top, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        # Búsqueda por nomenclatura
        row = 0
        ttk.Label(main, text="Nomenclatura:").grid(row=row, column=0, sticky="e", **pad)
        self.var_nom = tk.StringVar()
        self.entry_nom = ttk.Entry(main, textvariable=self.var_nom, width=30)
        self.entry_nom.grid(row=row, column=1, sticky="w", **pad)
        ttk.Button(main, text="Buscar", command=self._buscar).grid(row=row, column=2, sticky="w", **pad)

        # Resultado existente
        row += 1
        self.frame_found = ttk.LabelFrame(main, text="Terreno encontrado", padding=8)
        self.frame_found.grid(row=row, column=0, columnspan=3, sticky="ew", **pad)
        self.frame_found.grid_remove()

        self.lbl_resumen = ttk.Label(self.frame_found, text="")
        self.lbl_resumen.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Button(self.frame_found, text="Vincular", command=self._vincular_existente).grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )

        # Alta de nuevo terreno
        row += 1
        self.frame_new = ttk.LabelFrame(main, text="Crear nuevo terreno", padding=8)
        self.frame_new.grid(row=row, column=0, columnspan=3, sticky="ew", **pad)
        self.frame_new.grid_remove()

        self.var_manzana = tk.StringVar()
        self.var_numero = tk.StringVar()
        self.var_sup = tk.StringVar()
        self.var_ubic = tk.StringVar()
        self.var_obs = tk.StringVar()

        # Nomenclatura (solo lectura) en alta
        ttk.Label(self.frame_new, text="Nomenclatura:").grid(row=0, column=0, sticky="e")
        self.lbl_nom_new = ttk.Label(self.frame_new, text="")
        self.lbl_nom_new.grid(row=0, column=1, sticky="w")

        ttk.Label(self.frame_new, text="Manzana:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self.frame_new, textvariable=self.var_manzana, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(self.frame_new, text="Nro. lote:").grid(row=2, column=0, sticky="e")
        ttk.Entry(self.frame_new, textvariable=self.var_numero, width=20).grid(row=2, column=1, sticky="w")

        ttk.Label(self.frame_new, text="Superficie:").grid(row=3, column=0, sticky="e")
        ttk.Entry(self.frame_new, textvariable=self.var_sup, width=20).grid(row=3, column=1, sticky="w")

        ttk.Label(self.frame_new, text="Ubicación:").grid(row=4, column=0, sticky="e")
        ttk.Entry(self.frame_new, textvariable=self.var_ubic, width=30).grid(row=4, column=1, sticky="w")

        ttk.Label(self.frame_new, text="Observaciones:").grid(row=5, column=0, sticky="e")
        ttk.Entry(self.frame_new, textvariable=self.var_obs, width=30).grid(row=5, column=1, sticky="w")

        ttk.Button(self.frame_new, text="Crear y vincular", command=self._crear_y_vincular).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        # Acciones de cierre
        ttk.Button(main, text="Cancelar", command=self._close).grid(row=row + 1, column=2, sticky="e", **pad)

    # ----- Acciones -----
    def _buscar(self) -> None:
        nom = self.var_nom.get().strip()
        if not nom:
            messagebox.showwarning("Atención", "Ingrese una nomenclatura.")
            return
        try:
            t = self.svc.buscar_por_nomenclatura(nom)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if t:
            resumen = f"ID {t.id} | Mz {t.manzana} - Lote {t.numero_lote} - {t.superficie} m2 - {t.estado}"
            self.lbl_resumen.configure(text=resumen)
            self._show_found()
        else:
            # Preparar alta con la nomenclatura buscada
            self.lbl_nom_new.configure(text=nom)
            self.var_manzana.set("")
            self.var_numero.set("")
            self.var_sup.set("")
            self.var_ubic.set("")
            self.var_obs.set("")
            self._show_new()

    def _show_found(self) -> None:
        self.frame_new.grid_remove()
        self.frame_found.grid()

    def _show_new(self) -> None:
        self.frame_found.grid_remove()
        self.frame_new.grid()

    def _vincular_existente(self) -> None:
        nom = self.var_nom.get().strip()
        t = self.svc.buscar_por_nomenclatura(nom)
        if not t or t.id is None:
            messagebox.showerror("Error", "No se pudo resolver el terreno.")
            return
        if self.on_select:
            self.on_select(int(t.id))
        self._close()

    def _crear_y_vincular(self) -> None:
        nom = self.lbl_nom_new.cget("text").strip()
        datos = {
            "nomenclatura": nom,
            "manzana": self.var_manzana.get().strip(),
            "numero_lote": self.var_numero.get().strip(),
            "superficie": self.var_sup.get().strip(),
            "ubicacion": self.var_ubic.get().strip(),
            "observaciones": self.var_obs.get().strip(),
        }
        try:
            new_id = self.svc.crear_con_nomenclatura(datos)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        if self.on_select:
            self.on_select(int(new_id))
        self._close()

    def _close(self) -> None:
        try:
            self.top.grab_release()
        except Exception:
            pass
        self.top.destroy()

