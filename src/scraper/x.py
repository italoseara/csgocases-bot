import json
import base64
import requests
from typing import Any

from .base import BaseScraper
from util.post import Post
from util.misc import USER_AGENT, X_API_KEY


class XScraper(BaseScraper):
    """A class to scrape X posts from a given account."""

    app: Any
    username: str
    auth_token: str
    csrf_token: str

    def __init__(self, app: Any, username: str, auth_token: str, csrf_token: str) -> None:
        super().__init__(app, username)

        self.auth_token = auth_token
        self.csrf_token = csrf_token

    def _get_user_id(self) -> str:
        """Get the user rest ID from the username."""

        url = "https://x.com/i/api/graphql/vqu78dKcEkW-UAYLw5rriA/useFetchProfileSections_canViewExpandedProfileQuery"

        headers = {
            "authorization": X_API_KEY,
            "user-agent": USER_AGENT,
            "x-csrf-token": self.csrf_token,
        }

        cookies = {
            "auth_token": self.auth_token,
            "ct0": self.csrf_token,
        }

        params = {
            "variables": json.dumps({
                "screenName": self.username,
            }),
        }

        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()

        user_id = response.json()["data"]["user_result_by_screen_name"]["id"]
        return base64.b64decode(user_id).decode("utf-8").removeprefix("UserResults:")

    def fetch_latest_post(self) -> Post:
        """Get the latest posts from the Facebook account."""

        url = f"https://x.com/i/api/graphql/Y9WM4Id6UcGFE8Z-hbnixw/UserTweets"

        self.app.log("Fetching latest X post...", end=" ")
        
        headers = {
            "authorization": X_API_KEY,
            "user-agent": USER_AGENT,
            "x-csrf-token": self.csrf_token,
        }

        cookies = {
            "auth_token": self.auth_token,
            "ct0": self.csrf_token,
        }

        params = {
            "variables": json.dumps({
                "userId": self._get_user_id(),
                "count": 20,
                "includePromotedContent": False,
                "withQuickPromoteEligibilityTweetFields": True,
                "withVoice": True,
                "withV2Timeline": True,
            }),
            "features": json.dumps({
                "profile_label_improvements_pcf_label_in_post_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "premium_content_api_read_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
                "responsive_web_grok_analyze_post_followups_enabled": True,
                "responsive_web_jetfuel_frame": False,
                "responsive_web_grok_share_attachment_enabled": True,
                "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "responsive_web_grok_analysis_button_from_backend": True,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_grok_image_annotation_enabled": False,
                "responsive_web_enhance_cards_enabled": False,
            }),
            "fieldToggles": json.dumps({
                "withArticlePlainText": False,
            }),
        }

        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()

        try:
            last_post = response.json()["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"][1]["entries"][0]\
                ["content"]

            if "itemContent" not in last_post:
                last_post = last_post["items"][0]["item"]

            last_post = last_post["itemContent"]["tweet_results"]["result"]["legacy"]

            last_post["user"] = {
                "screen_name": self.username,
                "url": f"https://x.com/{self.username}",
            }

            self.app.log("Success.", prefix="")

            return Post.from_x_post(last_post)
        except (KeyError, IndexError):
            self.app.log("Failed.", prefix="")
            return None