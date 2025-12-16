import os
import json
import requests
from datetime import datetime
from typing import Optional

from models import Post
from config import DEBUG, USER_AGENT


class DiscordAPI:
    BASE_MESSAGES_URL = "https://discord.com/api/v10/channels/{channel_id}/messages"

    def __init__(self) -> None:
        self.auth_token = os.getenv("DISCORD_AUTH_TOKEN")

    def fetch_latest_post(self, guild_id: str, channel_id: str) -> Optional[Post]:
        """Fetch the latest post from a Discord channel."""

        if DEBUG:  # Mock response for debugging
            with open("data/mock_discord_messages.json", "r", encoding="utf-8") as f:
                response = json.load(f)
        else:
            response = requests.get(
                self.BASE_MESSAGES_URL.format(channel_id=channel_id),
                headers={
                    "Authorization": self.auth_token,
                    "User-Agent": USER_AGENT,
                },
                params={"limit": 1},
            )
            if response.status_code != 200:
                return None

            response = response.json()

        if not response:
            return None

        latest_message = response[0]
        author_info = latest_message.get("author", {})
        author_username = author_info.get("username", "")
        author_url = f"https://discord.com/users/{author_info.get('id', '')}"

        return Post(
            platform="Discord",
            author=author_username,
            author_url=author_url,
            text=latest_message.get("content", ""),
            url=f"https://discord.com/channels/{guild_id}/{channel_id}/{latest_message.get('id', '')}",
            media_url=latest_message.get("attachments", [{}])[0].get("url", None),
            created_at=datetime.fromisoformat(latest_message.get("timestamp", "")),
        )
