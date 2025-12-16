import os
import json
import requests
import base64
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from tui.models import Post
from config import DEBUG, BEARER_TOKEN, USER_AGENT


load_dotenv()


class XTwitterAPI:
    BASE_USER_BY_SCREEN_NAME_URL = "https://x.com/i/api/graphql/vqu78dKcEkW-UAYLw5rriA/useFetchProfileSections_canViewExpandedProfileQuery"
    BASE_USER_TWEETS_URL = "https://x.com/i/api/graphql/Y9WM4Id6UcGFE8Z-hbnixw/UserTweets"

    def __init__(self) -> None:
        self.auth_token = os.getenv("X_AUTH_TOKEN")
        self.csrf_token = os.getenv("X_CSRF_TOKEN")

    def fetch_user_id(self, username: str) -> str:
        """Fetch user ID by username."""

        if DEBUG:  # Mock response for debugging
            with open("data/mock_x_user.json", "r", encoding="utf-8") as f:
                response = json.load(f)
        else:
            response = requests.get(
                self.BASE_USER_BY_SCREEN_NAME_URL,
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "User-Agent": USER_AGENT,
                    "X-CSRF-Token": self.csrf_token,
                },
                cookies={
                    "auth_token": self.auth_token,
                    "ct0": self.csrf_token,
                },
                params={
                    "variables": json.dumps({"screenName": username}),
                },
            )
            if response.status_code != 200:
                return ""

            response = response.json()

        user_id = response.get("data", {}).get("user_result_by_screen_name", {}).get("id", "")
        return base64.b64decode(user_id).decode("utf-8").removeprefix("UserResults:")

    def fetch_latest_post(self, username: str) -> Optional[Post]:
        """Fetch the latest post from a user by user ID."""

        if DEBUG:  # Mock response for debugging
            with open("data/mock_x_user_tweets.json", "r", encoding="utf-8") as f:
                response = json.load(f)
        else:
            headers = {
                "Authorization": f"Bearer {BEARER_TOKEN}",
                "User-Agent": USER_AGENT,
                "X-CSRF-Token": self.csrf_token,
            }

            cookies = {
                "auth_token": self.auth_token,
                "ct0": self.csrf_token,
            }

            params = {
                "variables": json.dumps(
                    {
                        "userId": self.fetch_user_id(username),
                        "count": 1,
                        "includePromotedContent": False,
                        "withQuickPromoteEligibilityTweetFields": True,
                        "withVoice": True,
                        "withV2Timeline": True,
                    }
                ),
                "features": json.dumps(
                    {
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
                    }
                ),
                "fieldToggles": json.dumps(
                    {
                        "withArticlePlainText": False,
                    }
                ),
            }

            response = requests.get(self.BASE_USER_TWEETS_URL, headers=headers, cookies=cookies, params=params)
            if response.status_code != 200:
                return None

            response = response.json()

        latest_tweet = (
            response.get("data", {})
            .get("user", {})
            .get("result", {})
            .get("timeline_v2", {})
            .get("timeline", {})
            .get("instructions", [])[1]
            .get("entries", [])[0]
            .get("content", {})
        )

        if "itemContent" not in latest_tweet:
            latest_tweet = latest_tweet.get("items", [])[0].get("item", {})

        latest_tweet = latest_tweet.get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("legacy", {})

        return Post(
            platform="X",
            author=username,
            author_url=f"https://x.com/{username}",
            text=latest_tweet.get("full_text", ""),
            url=latest_tweet.get("entities", {}).get("media", [{}])[0].get("url", ""),
            media_url=latest_tweet.get("entities", {}).get("media", [{}])[0].get("media_url_https", None),
            created_at=datetime.strptime(latest_tweet.get("created_at", ""), "%a %b %d %H:%M:%S %z %Y"),
            raw_data=latest_tweet,
        )
