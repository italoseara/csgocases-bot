from textual.widgets import RichLog, TabbedContent, TabPane, Static
from textual.app import ComposeResult

from textual.containers import Vertical


class AppBody(Vertical):
    """Main Body Container for the Application."""

    DEFAULT_CSS = """
    #logs-tab {
        height: 1fr;
        border: $secondary round;
        padding-left: 1;

        RichLog {
            scrollbar-size: 0 1;

            &:focus {
                background-tint: transparent;
            }
        }
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Logs", id="logs-tab"):
                yield RichLog(highlight=True, markup=True, wrap=True, max_lines=1000)
            with TabPane("Settings", id="settings-tab"):
                yield Static("Settings content area")
            with TabPane("Help", id="help-tab"):
                yield Static("Help content area")
