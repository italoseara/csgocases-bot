from textual.app import ComposeResult
from textual.widgets import Footer

from . import Countdown


class AppFooter(Footer):
    """Custom Footer for the Application."""

    DEFAULT_CSS = """
    Footer {
        background: transparent;
    }

    FooterKey > .footer-key--key {
        color: $primary;
        background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Countdown(5)
