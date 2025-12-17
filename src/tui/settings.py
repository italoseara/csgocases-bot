import json
from typing import Self
from dataclasses import dataclass


@dataclass
class Settings:
    SETTINGS_PATH = "settings.json"

    database_url: str = ""
    x_auth_token: str = ""
    x_csrf_token: str = ""
    discord_auth_token: str = ""
    enable_auto_redeem: bool = True
    enable_discord_scraper: bool = True
    enable_instagram_scraper: bool = True
    enable_x_scraper: bool = True
    enable_facebook_scraper: bool = True
    send_notifications: bool = True

    @classmethod
    def load(cls) -> Self:
        # Load settings from a file or other source

        try:
            with open(cls.SETTINGS_PATH, "r") as f:
                settings = json.load(f)
            return cls(**settings)
        except FileNotFoundError:
            return cls()
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding settings file: {e}")

    def save(self) -> None:
        # Save settings to a file or other destination

        try:
            with open(self.SETTINGS_PATH, "w") as f:
                json.dump(self.__dict__, f, indent=4)
        except Exception as e:
            raise IOError(f"Error saving settings file: {e}")
