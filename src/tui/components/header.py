from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widgets import Label


class AppHeader(Horizontal):
    """Custom Header for the Application."""

    DEFAULT_CSS = """
    AppHeader {
        dock: top;
        height: 1;
        margin-bottom: 1;
        width: 100%;
        background: transparent;
    }

    #app-title {
        width: 1fr;
        text-align: left;
        color: $primary;
    }

    #app-status {
        width: auto;
        text-align: right;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("[b]CSGOCASES Promocode Scraper[/] [dim]v0.1.0[/]", id="app-title")
        yield Label("[dim]Not logged in[/]", id="app-status")
