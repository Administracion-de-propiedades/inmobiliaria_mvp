from __future__ import annotations

import tkinter as tk
from typing import Type, Any

from config.settings import configure_logging, get_settings
from core.frame_manager import FrameManager, BaseScreen
from view.login_screen import LoginScreen


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        settings = get_settings()
        configure_logging()

        self.title(settings.app_title)
        # Ampliar tamaño por pantallas de ABM
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Container único para pantallas
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Router
        self.router = FrameManager(self.container, self)

        # Pantalla inicial
        self.show_screen(LoginScreen)

    # ---- Navegación pública (compat con pantallas existentes) ----
    def show_screen(self, screen_class: Type[BaseScreen], *args: Any, **kwargs: Any) -> BaseScreen:
        return self.router.show_screen(screen_class, *args, **kwargs)

    def go_back(self) -> None:
        self.router.go_back()


def main() -> None:
    app = App()
    # Info diagnóstica de DB
    s = get_settings()
    print(f"ENV: {s.env}")
    print(f"DB_ENGINE: {s.db_engine}")
    if s.db_engine == "sqlite":
        print(f"DB_PATH: {s.sqlite_path}")
    else:
        print(f"DB_HOST: {s.db_host}:{s.db_port} DB_NAME: {s.db_name}")
    app.mainloop()


if __name__ == "__main__":
    main()

