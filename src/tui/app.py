from rich.text import Text
from datetime import datetime
from textual.theme import Theme
from textual.widgets import RichLog
from textual.binding import Binding
from textual.app import App, ComposeResult

from .components import AppFooter, AppHeader, AppBody


class CSGOCasesApp(App):
    """CSGOCases Promocode Bot TUI Application."""

    TITLE = "CSGOCases Bot"

    BINDINGS = [
        Binding(
            key="ctrl+q",
            action="app.quit",
            description="Quit",
            tooltip="Quit the application.",
            priority=True,
            id="quit",
        ),
        Binding(
            key="ctrl+s",
            action="force_scrape",
            description="Scrape",
            tooltip="Force a promocode scrape.",
            priority=True,
            id="force-scrape",
        ),
    ]

    CSS = """
    Screen {
        padding: 0 1;
        background: $background;
    }
    """

    def on_mount(self) -> None:
        self.register_theme(
            Theme(
                name="csgocases",
                primary="#1db954",
                secondary="#17a34a",
                accent="#22c55e",
                foreground="#e4e4e7",
                background="#0f1419",
                surface="#1a1f26",
                panel="#161b22",
            )
        )
        self.theme = "csgocases"

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield AppBody()
        yield AppFooter(show_command_palette=False, compact=True)

    def on_ready(self) -> None:
        """Called when the app is ready."""

        self.info("Application started.")

    def info(self, message: str) -> None:
        """Log an info message to the RichLog widget."""
        self._log("INFO", message)

    def debug(self, message: str = None) -> None:
        """Log a debug message to the RichLog widget."""
        self._log("DEBUG", message)

    def warn(self, message: str) -> None:
        """Log a warning message to the RichLog widget."""
        self._log("WARN", message)

    def error(self, message: str) -> None:
        """Log an error message to the RichLog widget."""
        self._log("ERROR", message)

    def success(self, message: str) -> None:
        """Log a success message to the RichLog widget."""
        self._log("SUCCESS", message)

    def _log(self, level: str, message: str) -> None:
        colors = {
            "INFO": "cyan",
            "DEBUG": "white",
            "WARN": "bright_yellow",
            "ERROR": "indian_red",
            "SUCCESS": "light_green",
        }

        ts = datetime.now().strftime("%H:%M:%S")
        color = colors.get(level.upper(), "white")

        log = self.query_one(RichLog)
        log.write(f"[{ts}] [bold {color}]{level:<8}[/] - {message}")
