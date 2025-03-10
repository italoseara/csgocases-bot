import tkinter as tk
from tkinter import ttk

from ui.webimage import WebImage


class User(tk.Frame):

    def __init__(self, master: tk.Misc, name: str, avatar_url: str, balance: float) -> None:
        super().__init__(master)

        self.name = name
        self.avatar_url = avatar_url
        self.balance = balance

        self.setup_ui()

    def setup_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.name_label = tk.Label(self, text=self.name, font=("TkDefaultFont", 12))
        self.name_label.grid(row=0, column=0, sticky=tk.SE, padx=(0, 10))

        self.balance_label = tk.Label(self, text=f"${self.balance:.2f}", font=("TkDefaultFont", 11), fg="green")
        self.balance_label.grid(row=1, column=0, sticky=tk.NE, padx=(0, 10))

        self.avatar_image = WebImage(self, url=self.avatar_url, width=50, height=50, rounded=True)
        self.avatar_image.grid(row=0, column=1, rowspan=2, sticky=tk.E)

    def set_name(self, name: str) -> None:
        self.name = name
        self.name_label.config(text=self.name)

    def set_avatar_url(self, avatar_url: str) -> None:
        self.avatar_url = avatar_url
        self.avatar_image.set_url(self.avatar_url)

    def set_balance(self, balance: float) -> None:
        self.balance = balance
        self.balance_label.config(text=f"${self.balance:.2f}")
