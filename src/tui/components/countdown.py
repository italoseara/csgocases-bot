import asyncio
from datetime import datetime, timedelta
from textual.widgets import Static


class Countdown(Static):
    """A simple countdown timer widget."""

    DEFAULT_CSS = """
    Countdown {
        color: $primary;
        dock: right;
        width: auto;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.remaining_seconds = 0
        self.running = True
        self.update_label()

    def update_label(self) -> None:
        if self.app.scraping:
            self.update("[b]Scraping...[/]")
            return

        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.update(f"[b]Next Scrape In:[/] {minutes:02}:{seconds:02}")

    async def on_mount(self) -> None:
        self.set_interval(1, self.tick)

    def tick(self) -> None:
        self.remaining_seconds = int((self.app.next_scrape - datetime.now()).total_seconds())
        self.remaining_seconds = max(0, self.remaining_seconds)
        self.update_label()

        if self.remaining_seconds == 0:
            if not self.app.scraping:
                asyncio.create_task(asyncio.to_thread(self.app.scrape))
                self.app.next_scrape = datetime.now() + timedelta(minutes=self.app.settings.scrape_interval)