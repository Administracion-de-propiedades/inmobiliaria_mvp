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

    current_frame: tk.Frame | None = None

    def show_dashboard() -> None:
        nonlocal current_frame
        if current_frame is not None:
            current_frame.destroy()
        current_frame = DashboardScreen(container)
        current_frame.pack(fill=tk.BOTH, expand=True)

    # Initial screen: Login
    current_frame = LoginScreen(container, auth_service=auth_service, on_success=show_dashboard)
    current_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

