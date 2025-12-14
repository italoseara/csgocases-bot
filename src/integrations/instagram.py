import json
import requests
from datetime import datetime
from typing import Optional, Any

from core.models import Post
from config import DEBUG


class InstagramAPI:
    BASE_PROFILE_API_ENDPOINT = "https://www.instagram.com/api/v1/users/web_profile_info/"

    def __init__(
        self,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        app_id: str = "936619743392459",
        server_id: str = "1031060024",
        default_timeout: float = 10.0,
    ) -> None:
        self.user_agent = user_agent
        self.app_id = app_id
        self.server_id = server_id
        self.default_timeout = default_timeout

    def fetch_profile(self, username: str, timeout: Optional[float] = None) -> Optional[dict[str, Any]]:
        if DEBUG:  # Mock response for debugging
            with open("data/mock_instagram_profile.json", "r", encoding="utf-8") as f:
                return json.load(f)

        resp = requests.get(
            self.BASE_PROFILE_API_ENDPOINT,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "X-IG-App-ID": self.app_id,
                "X-Instagram-AJAX": self.server_id,
            },
            params={"username": username},
            timeout=timeout or self.default_timeout,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        return data.get("data", {}).get("user", None)

    def fetch_latest_post(self, username: str, timeout: Optional[float] = None) -> Optional[Post]:
        profile = self.fetch_profile(username, timeout=timeout)
        if not profile:
            return None

        edges = profile.get("edge_owner_to_timeline_media", {}).get("edges", [])
        if not edges:
            return None

        latest_post = edges[0].get("node", None)
        return Post(
            platform="Instagram",
            author=username,
            text=latest_post.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", ""),
            url=f"https://www.instagram.com/p/{latest_post.get('shortcode', '')}/",
            media_url=latest_post.get("display_url", None),
            created_at=datetime.fromtimestamp(latest_post.get("taken_at_timestamp", 0)),
            raw_data=latest_post,
        )
