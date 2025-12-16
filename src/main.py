from config import DISCORD_GUILD_ID, DISCORD_CHANNEL_ID
from utils.ocr import read_promocode_from_image_url
from integrations import InstagramAPI, XTwitterAPI, DiscordAPI, FacebookAPI, CSGOCasesAPI


def main() -> None:
    client = CSGOCasesAPI()

    code = read_promocode_from_image_url(
        "https://instagram.fssa7-1.fna.fbcdn.net/v/t51.2885-15/574460163_18168037402373339_2058004655445433385_n.jpg?stp=dst-jpg_e15_fr_s1080x1080_tt6&_nc_ht=instagram.fssa7-1.fna.fbcdn.net&_nc_cat=111&_nc_oc=Q6cZ2QEiR-UdhrhWuy87ZbTM5p7qLtK9aaoUQtEgoLOzldH0_JOsUDvb0JN-nqIiEk4lEKPasYdIS_T7sII5gOqcDaG-&_nc_ohc=kqD2caK4DfsQ7kNvwFaY0pL&_nc_gid=lv_LyHGg1-yHx35t_-Ib9Q&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfnP5jUMiSQPv0fD0G494MJO7bfmcXReFrunYEOLPgNHBQ&oe=6944D4C5&_nc_sid=8b3546"
    )
    result = client.claim_promocode(code)
    print(f"Promocode claim result: {result}")


if __name__ == "__main__":
    main()
