import json
import requests
from datetime import datetime
from typing import Optional

from tui.models import Post
from config import DEBUG, USER_AGENT
from utils.soup import extract_json_objects_containing_key, deep_find


class FacebookAPI:
    BASE_URL = "https://www.facebook.com/{username}/"

    def __init__(self) -> None:
        pass

    def fetch_latest_post(self, username: str) -> Optional[Post]:
        if DEBUG:
            with open("data/mock_facebook_user.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            response = requests.get(
                self.BASE_URL.format(username=username),
                headers={
                    "Accept": "text/xhtml,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Sec-Fetch-Mode": "navigate",
                    "User-Agent": USER_AGENT,
                },
            )

            if response.status_code != 200:
                return None

            matches = extract_json_objects_containing_key(response.text, "timeline_list_feed_units")
            if not matches:
                return None

            matched = matches[0]  # Maybe improve later by selecting best match
            data = deep_find(matched, "user")
            if not data or not isinstance(data, dict):
                return None

        edges = data.get("timeline_list_feed_units", {}).get("edges", [])
        if not edges:
            return None

        comet_sections = edges[0].get("node", {}).get("comet_sections", {})
        story = comet_sections.get("content", {}).get("story", {})

        return Post(
            platform="Facebook",
            author=story.get("actors", [])[0].get("name", "unknown"),
            author_url=story.get("actors", [])[0].get("url", ""),
            text=story.get("message", {}).get("text", ""),
            url=story.get("wwwURL", ""),
            media_url=story.get("attachments", [])[0]
            .get("styles", {})
            .get("attachment", {})
            .get("media", {})
            .get("photo_image", {})
            .get("uri", ""),
            created_at=datetime.fromtimestamp(comet_sections.get("timestamp", {}).get("story", {}).get("creation_time", 0)),
            raw_data=data,
        )
