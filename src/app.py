from __future__ import annotations

import tkinter as tk

from config.settings import configure_logging, get_settings
from services.auth_service import AuthService
from view.dashboard_screen import DashboardScreen
from view.login_screen import LoginScreen


def main() -> None:
    """Entry point for the Inmobiliaria MVP application."""
    # Load settings and configure logging early
    settings = get_settings()
    configure_logging()

    # Diagnostic info
    print(f"ENV: {settings.env}")
    print(f"DB_ENGINE: {settings.db_engine}")
    if settings.db_engine == "sqlite":
        print(f"DB_PATH: {settings.sqlite_path}")
    else:
        print(f"DB_HOST: {settings.db_host}:{settings.db_port} DB_NAME: {settings.db_name}")

    root = tk.Tk()
    root.title(settings.app_title)
    root.geometry("420x220")
    root.minsize(380, 200)

    auth_service = AuthService()

    container = tk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True)

    class AppController:
        def __init__(self, container: tk.Misc):
            self.container = container
            self.current_frame: tk.Frame | None = None

        def _mount(self, frame: tk.Frame) -> None:
            if self.current_frame is not None:
                try:
                    self.current_frame.destroy()
                except Exception:
                    pass
            self.current_frame = frame
            self.current_frame.pack(fill=tk.BOTH, expand=True)

        def show_dashboard(self, _user=None) -> None:
            self._mount(DashboardScreen(self.container, app=self))

        def show_screen(self, screen_cls, *args, **kwargs) -> None:
            # Instantiate with (parent, app)
            try:
                frame = screen_cls(self.container, app=self, *args, **kwargs)
            except TypeError:
                frame = screen_cls(self.container, self)
            self._mount(frame)

        def go_back(self) -> None:
            self.show_dashboard()

    app = AppController(container)

    # Initial screen: Login
    app.current_frame = LoginScreen(container, auth_service=auth_service, on_success=app.show_dashboard, app=app)
    app.current_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

