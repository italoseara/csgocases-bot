import asyncio
from textual.theme import Theme
from textual.widgets import RichLog
from textual.binding import Binding
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from discord_webhook import DiscordWebhook, DiscordEmbed

from models.post import Post
from utils.ocr import read_promocode_from_image_url
from repositories.promocode import PromocodeRepository
from integrations import CSGOCasesAPI, FacebookAPI, XTwitterAPI, DiscordAPI, InstagramAPI
from .components import AppFooter, AppHeader, AppBody
from .settings import Settings

from config import X_USERNAME, DISCORD_CHANNEL_ID, DISCORD_GUILD_ID, INSTAGRAM_USERNAME, FACEBOOK_USERNAME


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
            description="Force Scrape",
            tooltip="Force a promocode scrape.",
            priority=True,
            id="force-scrape",
        ),
        Binding(
            key="ctrl+r",
            action="restart_countdown",
            description="Restart Countdown",
            tooltip="Restart the scrape countdown timer.",
            priority=True,
            id="restart-countdown",
        ),
    ]

    CSS = """
    Screen {
        padding: 0 1;
        background: $background;
    }
    """

    scraping = False
    settings = Settings.load()
    next_scrape = datetime.now() + timedelta(minutes=settings.scrape_interval)

    bot = CSGOCasesAPI()
    promocode_repo = PromocodeRepository(settings.database_url)

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

    def on_shutdown(self) -> None:
        """Called when the app is shutting down."""

        self.info("Shutting down application...")
        self.bot.quit()

    def action_restart_countdown(self) -> None:
        """Restart the scrape countdown timer."""

        self.next_scrape = datetime.now() + timedelta(minutes=self.settings.scrape_interval)
        self.info("Scrape countdown timer restarted.")

    def action_force_scrape(self) -> None:
        """Force a promocode scrape."""

        if self.scraping:
            self.warn("A scrape is already in progress. Please wait...")
            return

        self.info("Forcing promocode scrape...")

        try:
            asyncio.create_task(asyncio.to_thread(self.scrape))
        finally:
            self.next_scrape = datetime.now() + timedelta(minutes=self.settings.scrape_interval)

    def scrape(self) -> None:
        """Perform a promocode scrape."""

        self.scraping = True
        self.info("Starting promocode scrape...")

        posts: list[Post] = []

        self.info("Scraping X (Twitter)...")
        posts.append(
            XTwitterAPI(
                auth_token=self.settings.x_auth_token,
                csrf_token=self.settings.x_csrf_token,
            ).fetch_latest_post(X_USERNAME)
        )

        self.info("Scraping Discord...")
        posts.append(
            DiscordAPI(
                auth_token=self.settings.discord_auth_token,
            ).fetch_latest_post(DISCORD_GUILD_ID, DISCORD_CHANNEL_ID)
        )

        self.info("Scraping Facebook...")
        posts.append(FacebookAPI().fetch_latest_post(FACEBOOK_USERNAME))

        self.info("Scraping Instagram...")
        posts.append(InstagramAPI().fetch_latest_post(INSTAGRAM_USERNAME))

        self.info("Analyzing posts...")
        for post in posts:
            if post is None:
                continue

            self.debug(f"Analyzing post from {post.platform}...")
            if not post.media_url:
                self.warn(f"No media found in post from {post.platform}. Skipping...")
                continue

            # Check if there is the word "promocode" in the post text
            if post.text and "promocode" not in post.text.lower():
                self.info(f"No promocode mentioned in post from {post.platform}. Skipping...")
                continue

            # Check if promocode already exists
            if self.promocode_repo.exists_by_post_url(post.url):
                self.info(f"Promocode from post on {post.platform} already claimed. Skipping...")
                continue

            promocode = read_promocode_from_image_url(post.media_url)
            if not promocode:
                self.warn(f"No promocode found in post from {post.platform}.")
                continue

            # Redeem promocode if auto-redeem is enabled
            if self.settings.enable_auto_redeem:
                if not self.bot._is_logged_in:
                    self.error("Bot is not logged in. Cannot claim promocode.")
                    continue

                self.info(f"Promocode '{promocode}' found in post from {post.platform}. Claiming...")
                try:
                    result = self.bot.claim_promocode(promocode)
                    if result.get("status") == "success":
                        self.success(f"Promocode '{promocode}' claimed successfully: {result.get('message')}")
                    else:
                        self.error(f"Failed to claim promocode '{promocode}': {result.get('message')}")
                    self.promocode_repo.create(code=promocode, post_url=post.url)

                except Exception as e:
                    self.error(f"Failed to claim promocode '{promocode}': {e}")

            # Notify via Discord if enabled
            if self.settings.send_notifications:
                webhook_url = self.settings.discord_webhook_url
                if not webhook_url:
                    self.warn("Discord webhook URL is not set. Cannot send notification.")
                    continue

                self.info(f"Sending notification for promocode '{promocode}'...")
                try:
                    webhook = DiscordWebhook(url=webhook_url, content="@everyone")

                    embed = DiscordEmbed(
                        title=f"New promocode `{promocode}`",
                        description=f"Click [here]({post.url}) to see the post",
                        color="6dc176",
                    )
                    embed.set_author(
                        name="csgocases.com", icon_url="https://csgocases.com/images/avatar.jpg", url=post.author_url
                    )
                    embed.set_image(url=post.media_url)
                    embed.set_timestamp()

                    webhook.add_embed(embed)

                    response = webhook.execute()
                    if response.ok:
                        self.success(f"Notification for promocode '{promocode}' sent successfully.")
                    else:
                        self.error(
                            f"Failed to send notification for promocode '{promocode}': {response.status_code} {response.reason}"
                        )

                except Exception as e:
                    self.error(f"Failed to send notification for promocode '{promocode}': {e}")

        self.info("Promocode scrape completed.")
        self.scraping = False

    def info(self, message: str) -> None:
        """Log an info message to the RichLog widget."""
        self.__log("INFO", message)

    def debug(self, message: str) -> None:
        """Log a debug message to the RichLog widget."""
        self.__log("DEBUG", message)

    def warn(self, message: str) -> None:
        """Log a warning message to the RichLog widget."""
        self.__log("WARN", message)

    def error(self, message: str) -> None:
        """Log an error message to the RichLog widget."""
        self.__log("ERROR", message)

    def success(self, message: str) -> None:
        """Log a success message to the RichLog widget."""
        self.__log("SUCCESS", message)

    def __log(self, level: str, message: str) -> None:
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
