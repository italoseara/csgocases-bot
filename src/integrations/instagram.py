import json
import requests
from datetime import datetime
from typing import Optional, Any

from models import Post
from config import DEBUG, USER_AGENT


class InstagramAPI:
    BASE_PROFILE_API_ENDPOINT = "https://www.instagram.com/api/v1/users/web_profile_info/"

    def __init__(
        self,
        app_id: str = "936619743392459",
        server_id: str = "1031060024",
    ) -> None:
        self.app_id = app_id
        self.server_id = server_id

    def fetch_profile(self, username: str) -> Optional[dict[str, Any]]:
        if DEBUG:  # Mock response for debugging
            with open("data/mock_instagram_profile.json", "r", encoding="utf-8") as f:
                response = json.load(f)
        else:
            response = requests.get(
                self.BASE_PROFILE_API_ENDPOINT,
                headers={
                    "User-Agent": USER_AGENT,
                    "X-IG-App-ID": self.app_id,
                    "X-Instagram-AJAX": self.server_id,
                },
                params={"username": username},
            )
            if response.status_code != 200:
                return None

            response = response.json()

        return response.get("data", {}).get("user", None)

    def fetch_latest_post(self, username: str) -> Optional[Post]:
        profile = self.fetch_profile(username)
        if not profile:
            return None

        edges = profile.get("edge_owner_to_timeline_media", {}).get("edges", [])
        if not edges:
            return None

        latest_post = edges[0].get("node", None)
        return Post(
            platform="Instagram",
            author=username,
            author_url=f"https://www.instagram.com/{username}/",
            text=latest_post.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", ""),
            url=f"https://www.instagram.com/p/{latest_post.get('shortcode', '')}/",
            media_url=latest_post.get("display_url", None),
            created_at=datetime.fromtimestamp(latest_post.get("taken_at_timestamp", 0)),
            raw_data=latest_post,
        )
