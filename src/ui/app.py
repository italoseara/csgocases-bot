import os
import json
import platform
import threading
import tkinter as tk
import sv_ttk as svtk  # Only used to set the theme
from tkinter import ttk
from datetime import datetime
from seleniumbase import Driver

import bypass
from bot import Bot
from ui.user import User
from ui.entry_with_label import EntryWithlabel


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        w, h = 800, 540
        if platform.system() == "Windows":
            w, h = w + 51, h + 31  # Fix inconsistencies in window size

        self.title("Promocode Scraper")
        self.geometry(f"{w}x{h}")
        self.minsize(w, h)

        self.setup_ui()

        self.bot = None
        self.driver = Driver(uc=True, headless=True)

    def run(self) -> None:
        """Runs the application."""

        svtk.set_theme("light")
        self.load_config()
        
        self.bot = Bot(self)
        self.mainloop()
        
    def destroy(self):
        self.save_config()
        super().destroy()

    def get_values(self) -> dict:
        """Returns the configuration values from the UI."""

        return {
            "x_auth_token": self.x_auth_token.get(),
            "x_csrf_token": self.x_csrf_token.get(),
            "discord_api_key": self.discord_api_key.get(),
            "discord_webhook": self.discord_webhook.get(),
            "cspro_cookie": self.cspro_cookie.get(),
            "dark_mode": self.dark_mode.get(),
            "start_with_os": self.start_with_os.get(),
            "start_minimized": self.start_minimized.get()
        }

    def save_config(self) -> None:
        """Saves the configuration values to a file."""

        if not os.path.exists("data"):
            os.makedirs("data")

        with open("data/config.json", "w") as file:
            json.dump(self.get_values(), file, indent=2)

    def load_config(self) -> None:
        """Loads the configuration values from a file."""

        if not os.path.exists("data/config.json"):
            return

        with open("data/config.json", "r") as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                return

            self.x_auth_token.set(config.get("x_auth_token", ""))
            self.x_csrf_token.set(config.get("x_csrf_token", ""))
            self.discord_api_key.set(config.get("discord_api_key", ""))
            self.discord_webhook.set(config.get("discord_webhook", ""))
            self.cspro_cookie.set(config.get("cspro_cookie", ""))

            self.dark_mode.set(config.get("dark_mode", False))
            self.start_with_os.set(config.get("start_with_os", True))
            self.start_minimized.set(config.get("start_minimized", True))

            svtk.set_theme("dark" if config.get("dark_mode", False) else "light")
            self.update_user()

    def force_start(self) -> None:
        """Starts the scraping process in a separate thread to prevent freezing."""

        threading.Thread(target=self.bot.run).start()

    def setup_ui(self) -> None:
        """Initialize and arrange all UI components."""

        left_frame = ttk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True)
        
        self.create_options_section(left_frame)
        self.create_credentials_section(left_frame)
        self.create_start_button(left_frame)

        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)

        top_right_frame = ttk.Frame(right_frame)
        top_right_frame.pack(side="top", fill="both", expand=True)

        self.create_user_section(top_right_frame)

        bottom_right_frame = ttk.Frame(right_frame)
        bottom_right_frame.pack(side="bottom", fill="both", expand=True)

        self.create_log_section(bottom_right_frame)

    def update_user(self, default: bool = False, value: str = None) -> None:
        if not hasattr(self, "user"):
            default_avatar_url = "https://avatars.steamstatic.com/b5bd56c1aa4644a474a2e4972be27ef9e82e517e_full.jpg"
            self.user = User(self.user_frame, "Not Found", default_avatar_url, 0.0)
            self.user.pack(fill="both", expand=True)

        def _update_user() -> None:
            self.log("Updating user information...")
            
            if not (cookie := value or self.cspro_cookie.get()):
                self.log("Cookie not found")
                return

            cookies = [{ "name": "sfRemember", "value": cookie }]
            response = bypass.get("https://csgocases.com/api.php/auth", cookies=cookies, driver=self.driver)

            if "success" not in response or not response["success"]:
                return

            username = response["user"]["nick"]
            balance = float(response["user"]["wallet"])

            self.user.set_name(username)
            self.user.set_balance(balance)
            self.user.set_avatar_url(response["user"]["avatar"])

            self.log(f"User information updated: {username} (${balance})")

        if not default:
            threading.Thread(target=_update_user).start()

    def create_user_section(self, frame: tk.Frame) -> None:
        """Creates the user section."""

        self.user_frame = ttk.Frame(frame)
        self.user_frame.pack(padx=15, pady=(20, 0), fill="y", expand=True, anchor="e")

        self.update_user(default=True)

    def create_credentials_section(self, frame: tk.Frame) -> None:
        """Creates the credentials input section."""

        credentials_frame = ttk.LabelFrame(frame, text="Credentials")
        credentials_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.x_auth_token = EntryWithlabel(credentials_frame, label="X Auth Token", secret=True)
        self.x_auth_token.pack(fill="x", padx=10, pady=5)

        self.x_csrf_token = EntryWithlabel(credentials_frame, label="X CSRF Token", secret=True)
        self.x_csrf_token.pack(fill="x", padx=10, pady=5)

        self.discord_api_key = EntryWithlabel(credentials_frame, label="Discord API Key", secret=True)
        self.discord_api_key.pack(fill="x", padx=10, pady=5)

        self.discord_webhook = EntryWithlabel(credentials_frame, label="Discord Webhook URL (Optional)", secret=True)
        self.discord_webhook.pack(fill="x", padx=10, pady=5)

        self.cspro_cookie = EntryWithlabel(credentials_frame, label="CS.PRO Cookie (Optional)", secret=True)
        self.cspro_cookie.pack(fill="x", padx=10, pady=5)
        self.cspro_cookie.entry.bind("<Control-v>", lambda event: self.update_user(value=self.clipboard_get()))

    def create_options_section(self, frame: tk.Frame) -> None:
        """Creates the options section."""
        
        options_frame = ttk.LabelFrame(frame, text="Options")
        options_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.dark_mode = tk.BooleanVar(value=False)
        self.chk_dark_mode = ttk.Checkbutton(
            options_frame,
            text="Dark Mode",
            variable=self.dark_mode,
            style="Switch.TCheckbutton",
            command=lambda: svtk.set_theme("dark" if self.dark_mode.get() else "light")
        )
        self.chk_dark_mode.pack(fill="x", padx=10, pady=5)

        self.start_with_os = tk.BooleanVar(value=True)
        self.chk_start_with_os = ttk.Checkbutton(
            options_frame,
            text="Start with OS",
            variable=self.start_with_os,
            style="Switch.TCheckbutton",
            command=lambda: print(self.start_with_os.get()) # TODO: Implement
        )
        self.chk_start_with_os.pack(fill="x", padx=10, pady=5)

        self.start_minimized = tk.BooleanVar(value=True)
        self.chk_start_minimized = ttk.Checkbutton(
            options_frame,
            text="Start Minimized",
            variable=self.start_minimized,
            style="Switch.TCheckbutton",
            command=lambda: print(self.start_minimized.get()) # TODO: Implement
        )
        self.chk_start_minimized.pack(fill="x", padx=10, pady=5)

    def create_start_button(self, frame: tk.Frame) -> None:
        """Creates the start button."""
        
        start_button = ttk.Button(frame, text="Force Start", command=self.force_start, style="Accent.TButton")
        start_button.pack(fill="x", padx=10, pady=10)

    def create_log_section(self, frame: tk.Frame) -> None:
        """Creates the log section."""
        
        log_frame = ttk.LabelFrame(frame, text="Log")
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_section = tk.Text(log_frame, wrap="word", state="disabled", bd=0, font=("Consolas", 10))
        self.log("Promocode Scraper has started")
        self.log_section.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, message: str, end: str = "\n", prefix: str = f"[{datetime.now().strftime('%H:%M:%S')}] ") -> None:
        """Logs a message to the log section."""
        
        self.log_section.config(state="normal")
        self.log_section.insert(tk.END, f"{prefix}{message}{end}")
        self.log_section.config(state="disabled")
        self.log_section.see(tk.END)
