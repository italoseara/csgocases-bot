from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import RichLog, TabbedContent, TabPane, Static, Label, Input, Checkbox, MarkdownViewer

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

    #help-viewer {
        scrollbar-size: 0 1;
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
                help_text = """
                # CSGOCases Bot Help
                This application helps you automate the process of scraping and redeeming promocodes from various social media platforms for CSGOCases.

                ## Disclaimer
                Using bots to interact with websites may violate their terms of service. Use at your own risk, the author is not responsible for any misuse or damages caused by this software.

                ## Configuration
                - **Database URL**: The connection string for your database.
                - **Authentication Tokens**: Required tokens for accessing social media APIs.
                - **Bot Settings**: Options to enable/disable auto-redeeming and scrapers for different platforms.
                - **Scrape Interval**: How often the bot should check for new promocodes

                To find the `X Auth Token` and `X CSRF Token` for X (formerly Twitter), you can use your browser's developer tools while logged into your account. Look for `auth_token` and `ct0` cookies respectively in the storage section.

                To find the `Discord Auth Token`, you can use your browser's developer tools while logged into your Discord account. Look for `Authorization` header in the network requests.

                ## Usage
                1. Configure your settings in the 'Settings' tab.
                2. Monitor logs in the 'Logs' tab to see the bot's activity.
                3. Ensure your database is set up to store promocodes.

                ## Support
                For further assistance, please create an issue on the [GitHub repository](https://github.com/italoseara/csgocases-bot)

                ## Author
                This bot is developed and maintained by [Italo Seara](https://github.com/italoseara).
                """.replace(
                    " " * 16, ""
                )

                yield MarkdownViewer(help_text, show_table_of_contents=False, id="help-viewer")

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
