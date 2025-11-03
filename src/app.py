from __future__ import annotations

import tkinter as tk

from config.settings import settings
from services.auth_service import AuthService
from view.dashboard_screen import DashboardScreen
from view.login_screen import LoginScreen


def main() -> None:
    """Entry point for the Inmobiliaria MVP application."""
    root = tk.Tk()
    root.title(settings.APP_TITLE)
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

