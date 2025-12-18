from textual.containers import Vertical, Horizontal
from textual.widgets import RichLog, TabbedContent, TabPane, Static, Label, Input, Checkbox
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

    .container {
        border: $secondary round;
        padding: 0 1;
        height: 1fr;
    }

    #scrape_interval {
        margin-left: 1;
    }

    #db-area {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Logs", id="logs-tab"):
                yield RichLog(highlight=True, markup=True, wrap=True, max_lines=1000)

            with TabPane("Settings", id="settings-tab"):
                settings = self.app.settings

                with Horizontal():
                    with Vertical():
                        with Vertical(classes="container", id="db-area") as db_area:
                            db_area.border_title = "Database"

                            yield Label("URL:")
                            yield Input(
                                placeholder="e.g., postgresql://user:pass@loc...",
                                password=True,
                                compact=True,
                                id="database_url",
                                value=settings.database_url,
                            )

                        with Vertical(classes="container") as auth_area:
                            auth_area.border_title = "Authentication"

                            yield Label("X Auth Token:")
                            yield Input(
                                placeholder="Enter your X Auth Token here",
                                password=True,
                                compact=True,
                                id="x_auth_token",
                                value=settings.x_auth_token,
                            )

                            yield Static()
                            yield Label("X CSRF Token:")
                            yield Input(
                                placeholder="Enter your X CSRF Token here",
                                password=True,
                                compact=True,
                                id="x_csrf_token",
                                value=settings.x_csrf_token,
                            )

                            yield Static()
                            yield Label("Discord Auth Token:")
                            yield Input(
                                placeholder="Enter your Discord Auth Token here",
                                password=True,
                                compact=True,
                                id="discord_auth_token",
                                value=settings.discord_auth_token,
                            )

                    with Vertical(classes="container") as bot_area:
                        bot_area.border_title = "Bot Settings"

                        yield Checkbox(
                            label="Enable Auto-Redeem", value=settings.enable_auto_redeem, compact=True, id="enable_auto_redeem"
                        )

                        yield Static()
                        yield Checkbox(
                            label="Enable Discord Scraper",
                            value=settings.enable_discord_scraper,
                            compact=True,
                            id="enable_discord_scraper",
                        )
                        yield Checkbox(
                            label="Enable Instagram Scraper",
                            value=settings.enable_instagram_scraper,
                            compact=True,
                            id="enable_instagram_scraper",
                        )
                        yield Checkbox(
                            label="Enable X (Twitter) Scraper",
                            value=settings.enable_x_scraper,
                            compact=True,
                            id="enable_x_scraper",
                        )
                        yield Checkbox(
                            label="Enable Facebook Scraper",
                            value=settings.enable_facebook_scraper,
                            compact=True,
                            id="enable_facebook_scraper",
                        )

                        yield Static()
                        yield Checkbox(
                            label="Send Notifications to Discord",
                            value=settings.send_notifications,
                            compact=True,
                            id="send_notifications",
                        )

                        yield Static()
                        yield Label("Discord Webhook URL:")
                        yield Input(
                            placeholder="Enter your Webhook URL here",
                            password=True,
                            compact=True,
                            id="discord_webhook_url",
                            value=settings.discord_webhook_url,
                        )

                        yield Static()
                        with Horizontal():
                            yield Label("Scrape Interval (minutes):")
                            yield Input(
                                placeholder="e.g., 15",
                                compact=True,
                                id="scrape_interval",
                                value=str(settings.scrape_interval),
                                type="integer",
                            )

            with TabPane("Help", id="help-tab"):
                yield Static("Help content area")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""

        settings = self.app.settings

        if event.input.type == "integer":
            try:
                value = int(event.value)
            except ValueError:
                value = settings.__dict__[event.input.id]
            settings.__dict__[event.input.id] = value
        else:
            settings.__dict__[event.input.id] = event.value

        if event.input.id == "database_url":
            self.app.promocode_repo.url = event.value

        settings.save()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes."""

        settings = self.app.settings
        settings.__dict__[event.checkbox.id] = event.value
        settings.save()
