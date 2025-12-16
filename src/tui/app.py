from textual.app import App, ComposeResult
from textual.widgets import Footer, Static
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Label


class AppHeader(Horizontal):
    """Custom Header for the Application."""

    def compose(self) -> ComposeResult:
        yield Label("[b]CSGOCASES Promocode Scraper[/] [dim]v0.1.0[/]", id="app-title")
        yield Label("[dim]Not logged in[/]", id="app-status")


class CSGOCasesApp(App[str]):
    """CSGOCases Promocode Bot TUI Application."""

    TITLE = "CSGOCases Bot"
    SUB_TITLE = "1.0.0"

    def get_css_variables(self) -> dict[str, str]:
        """Override theme colors with CSGOCases branding."""
        variables = super().get_css_variables()
        variables.update({
            "primary": "#1db954",
            "secondary": "#17a34a",
            "accent": "#22c55e",
            "foreground": "#e4e4e7",
            "background": "#0f1419",
            "surface": "#1a1f26",
            "panel": "#242b33",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "success": "#1db954",
        })
        return variables

    BINDINGS = [
        Binding(
            key="f1",
            action="help",
            description="Help",
            tooltip="Show help information.",
            priority=True,
            id="help",
        ),
        Binding(
            key="ctrl+c",
            action="app.quit",
            description="Quit",
            tooltip="Quit the application.",
            priority=True,
            id="quit",
        ),
    ]

    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield Static("Main content area", id="main")
        yield Footer(show_command_palette=False, compact=True)

    def action_quit(self) -> None:
        self.exit()
