import io
import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw


class WebImage(tk.Label):
    def __init__(self, master: tk.Misc, url: str, width: int = 0, height: int = 0, rounded: bool = False) -> None:
        super().__init__(master)

        self.url = url
        self.width = width
        self.height = height
        self.rounded = rounded

        self.setup_ui()

    def setup_ui(self) -> None:
        response = requests.get(self.url)
        image = Image.open(io.BytesIO(response.content))

        if self.width > 0 and self.height > 0:
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        if self.rounded:
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, self.width, self.height), fill=255)

            image.putalpha(mask)
            image = image.convert("RGBA")

        self.image = ImageTk.PhotoImage(image)
        self.configure(image=self.image)

    def set_url(self, url: str) -> None:
        self.url = url
        self.setup_ui()
