import os
import json
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import Any

import bypass
from promocode import PromocodeReader
from util.post import Post
from scraper import *

load_dotenv()


class Bot:
    def __init__(self, app: Any) -> None:
        self.app = app

        x_auth_token = self.app.x_auth_token.get()
        x_csrf_token = self.app.x_csrf_token.get()
        discord_api_key = self.app.discord_api_key.get()

        if x_auth_token and x_csrf_token and discord_api_key:
            self.app.log("Configuration values loaded")
            self.enabled = True
        else:
            self.app.log("No configuration values found")
            self.enabled = False
        
        self.scrapers = [
            # Instagram is very strict with scraping se we need to remember to not abuse it
            IGScraper(self.app, username=os.getenv("IG_USERNAME")),

            FBScraper(self.app, username=os.getenv("FB_USERNAME")),
            
            XScraper(self.app, 
                     username=os.getenv("X_USERNAME"),
                     auth_token=x_auth_token,
                     csrf_token=x_csrf_token),
            
            DCScraper(self.app, 
                      guild_id=os.getenv("DISCORD_GUILD_ID"),
                      channel_id=os.getenv("DISCORD_CHANNEL_ID"),
                      api_key=discord_api_key)
        ]

    def run(self) -> None:
        if not self.enabled:
            self.app.log("Cannot run the bot without configuration values")
            return
        
        self.app.log("Bot is running")
        
        latest_posts = [scraper.fetch_latest_post() for scraper in self.scrapers]
        promocode_posts = [post for post in latest_posts 
                           if post is not None and 
                           "promocode" in post.text.lower()]

        expired_promocodes = self.load_expired_promocodes()
        new_promocodes = self.extract_valid_promocodes(promocode_posts, expired_promocodes)

        self.update_expired_promocodes(expired_promocodes, new_promocodes)

        for promocode, post in new_promocodes:
            self.app.log(f"New promocode found: {promocode}")
            self.broadcast(promocode, post)
            self.activate_promocode(promocode)

        self.app.log("Bot has finished running")

    def activate_promocode(self, promocode: str) -> None:
        self.app.log(f"Activating promocode `{promocode}`")

        if not self.app.cspro_cookie.get():
            self.app.log("No cookie provided. Skipping activation.")
            return
        
        url = "https://csgocases.com/api.php/add_wallet_code"
        cookies = [{ "name": "sfRemember", "value": self.app.cspro_cookie.get() }]

        response = bypass.get(url, cookies=cookies, params={"code": promocode}, driver=self.app.driver)
        if response is None:
            return

        if "wallet" in response:
            new_balance = float(response["wallet"])
            self.app.log(f"Promocode `{promocode}` successfully activated")
            self.app.log(response["message"])
            self.app.log(f"New balance: ${new_balance:.2f}")

            self.app.user.set_balance(new_balance)
        else:
            self.app.log(f"Could not activate promocode `{promocode}`")

            if "message" in response:
                self.app.log(response["message"])

    def broadcast(self, promocode: str, post: Post) -> None:
        webhook_url = self.app.discord_webhook.get()
        if not webhook_url:
            self.app.log("No webhook URL provided. Skipping broadcast.")
            return
        
        webhook = DiscordWebhook(url=webhook_url, content='@everyone')

        embed = DiscordEmbed(title=f"New promocode `{promocode}`", description=f"Click [here]({post.url}) to see the post", color="6dc176")
        embed.set_author(name="csgocases.com", 
                        icon_url="https://csgocases.com/images/avatar.jpg", 
                        url=post.author_url)
        embed.set_image(url=post.image_url)
        embed.set_timestamp()

        webhook.add_embed(embed)
        
        response = webhook.execute()
        if response.ok:
            self.app.log('Webhook message sent')
        else:
            self.app.log('Could not send the webhook message')

    def load_expired_promocodes(self) -> list[str]:
        if os.path.exists("data/promocodes.json"):
            with open("data/promocodes.json", "r") as file:
                return json.load(file)
        return []

    def extract_valid_promocodes(self, posts: list[Post], expired_promocodes: list[str]) -> list[tuple[str, Post]]:
        return [
            (code, post) for post in posts
            if (code := PromocodeReader(post.image).extract()) not in expired_promocodes
        ]

    def update_expired_promocodes(self, expired_promocodes: list[str], new_promocodes: list[tuple]) -> None:
        expired_promocodes.extend(code for code, _ in new_promocodes)
        with open("data/promocodes.json", "w") as file:
            json.dump(expired_promocodes, file)
