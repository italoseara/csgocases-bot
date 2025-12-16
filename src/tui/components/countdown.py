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

    def __init__(self, total_seconds: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.running = True
        self.update_label()

    def update_label(self) -> None:
        if self.remaining_seconds <= 0:
            self.update("[b]Scraping...[/]")
            return

        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.update(f"[b]Next Scrape In:[/] {minutes:02}:{seconds:02}")

    async def on_mount(self) -> None:
        self.set_interval(1, self.tick)

    def tick(self) -> None:
        if self.running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_label()
        elif self.remaining_seconds == 0:
            self.running = False
