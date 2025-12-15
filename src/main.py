import json
from core.models import Promocode
from integrations import InstagramAPI, XTwitterAPI, DiscordAPI, FacebookAPI
from config import DISCORD_GUILD_ID, DISCORD_CHANNEL_ID


def main() -> None:
    client = FacebookAPI()
    post = client.fetch_latest_post("csgocasescom")
    print(post)


if __name__ == "__main__":
    main()
