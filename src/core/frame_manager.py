from __future__ import annotations

import tkinter as tk
from typing import Type, Any, List, Optional, Dict


class BaseScreen(tk.Frame):
    """
    Base para todas las pantallas.
    Los screens pueden sobrescribir on_show/on_hide para cargar datos, focus, etc.
    """

    def on_show(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
        """Hook: se llama cuando la pantalla se vuelve visible."""
        pass

    def on_hide(self) -> None:  # noqa: D401
        """Hook: se llama justo antes de ocultar la pantalla."""
        pass


class FrameManager:
    """
    Router de pantallas con stack. Mantiene el estado de cada Frame.
    - push: crea/obtiene instancia del screen, oculta el actual y muestra el nuevo
    - pop: oculta el actual, muestra el anterior
    - replace: reemplaza la pantalla actual (opcional)
    """

    def __init__(self, container: tk.Widget, app: Any) -> None:
        self.container = container
        self.app = app
        self._stack: List[BaseScreen] = []
        # cache por clase -> instancia única (reutiliza pantalla)
        self._cache: Dict[Type[BaseScreen], BaseScreen] = {}

        # Layout: el container debe expandir
        if isinstance(container, (tk.Tk, tk.Toplevel, tk.Frame)):
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

    def _get_or_create(self, screen_class: Type[BaseScreen], *args: Any, **kwargs: Any) -> BaseScreen:
        # Reutiliza instancia por clase; si necesitás instancias múltiples por clase, cambiar esta estrategia.
        scr = self._cache.get(screen_class)
        if scr is None:
            scr = screen_class(self.container, self.app, *args, **kwargs)  # type: ignore[misc]
            self._cache[screen_class] = scr
            # Colocar en el grid una sola vez
            scr.grid(row=0, column=0, sticky="nsew")
        return scr

    def current(self) -> Optional[BaseScreen]:
        return self._stack[-1] if self._stack else None

    # --- Navegación ---
    def push(self, screen_class: Type[BaseScreen], *args: Any, **kwargs: Any) -> BaseScreen:
        """Muestra una pantalla encima de la pila, preservando la anterior."""
        # ocultar actual
        current = self.current()
        if current is not None:
            # Llamar hook si existe
            getattr(current, "on_hide", lambda: None)()
            current.grid_remove()

        # obtener/crear target
        target = self._get_or_create(screen_class, *args, **kwargs)
        # pasar parámetros a on_show si existe
        getattr(target, "on_show", lambda *a, **k: None)(*args, **kwargs)
        target.grid()  # vuelve a mostrarse en su misma celda
        self._stack.append(target)
        return target

    def pop(self) -> Optional[BaseScreen]:
        """Vuelve a la pantalla anterior (si existe)."""
        if len(self._stack) <= 1:
            # nada que hacer si no hay pantallas debajo
            return self.current()

        top = self._stack.pop()
        # ocultar la actual
        getattr(top, "on_hide", lambda: None)()
        top.grid_remove()

        # mostrar la anterior
        prev = self._stack[-1]
        getattr(prev, "on_show", lambda: None)()
        prev.grid()
        return prev

    def replace(self, screen_class: Type[BaseScreen], *args: Any, **kwargs: Any) -> BaseScreen:
        """Reemplaza la pantalla actual por otra (no aumenta profundidad del stack)."""
        if self._stack:
            current = self._stack.pop()
            getattr(current, "on_hide", lambda: None)()
            current.grid_remove()

        target = self._get_or_create(screen_class, *args, **kwargs)
        getattr(target, "on_show", lambda *a, **k: None)(*args, **kwargs)
        target.grid()
        self._stack.append(target)
        return target

    # Accesos auxiliares para la app
    def show_screen(self, screen_class: Type[BaseScreen], *args: Any, **kwargs: Any) -> BaseScreen:
        """Alias de push para compatibilidad con código existente."""
        return self.push(screen_class, *args, **kwargs)

    def go_back(self) -> Optional[BaseScreen]:
        """Alias de pop para compatibilidad con código existente."""
        return self.pop()
