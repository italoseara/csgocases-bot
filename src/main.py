from core.models import Promocode
from integrations.instagram import InstagramAPI


def main() -> None:
    # promocode = Promocode(
    #     "https://x.com/csgocasescom/status/1998825144442089497/photo/1",
    #     "https://pbs.twimg.com/media/G71A30pXMAA88Uv?format=jpg&name=medium",
    # )
    # print(promocode.code)
    client = InstagramAPI()
    profile = client.fetch_latest_post("csgocasescom")
    print(profile)


if __name__ == "__main__":
    main()
