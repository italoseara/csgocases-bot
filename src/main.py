import json
from core.models import Promocode
from integrations import InstagramAPI, XTwitterAPI, DiscordAPI
from config import DISCORD_GUILD_ID, DISCORD_CHANNEL_ID


def main() -> None:
    client = DiscordAPI()
    post = client.fetch_latest_post(DISCORD_GUILD_ID, DISCORD_CHANNEL_ID)
    print(post)


if __name__ == "__main__":
    main()
