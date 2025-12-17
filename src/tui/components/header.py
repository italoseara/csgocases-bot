import asyncio
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Button


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

    #login-btn {
        text-align: right;
        padding: 0;
        margin: 0;
        background: transparent;

        &:hover, &:focus {
            background: transparent;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("[b]CSGOCASES Promocode Scraper[/] [dim]v0.1.0[/]", id="app-title")
        login_btn = Button("[dim]\\[ Click to Log-in ][/]", id="login-btn", compact=True)
        login_btn.can_focus = False
        yield login_btn

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "login-btn":
            return

        btn = event.button
        btn.label = "Loading..."
        btn.disabled = True
        btn.refresh()  # force redraw in Textual

        try:
            logged_in = await asyncio.to_thread(self.app.bot.is_logged_in)

            while not logged_in:
                await asyncio.to_thread(self.app.bot.login)
                logged_in = await asyncio.to_thread(self.app.bot.is_logged_in)

            btn.label = f"[white]Logged in as: [#1db954]{self.app.bot.username}[/]"
            btn.disabled = True

        except Exception as exc:
            btn.label = "[red]Login Failed[/]"
            self.app.error(f"Login check failed: {exc}")

        finally:
            btn.disabled = False
            btn.refresh()
