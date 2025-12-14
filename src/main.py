import json
from core.models import Promocode
from integrations import InstagramAPI, XTwitterAPI


def main() -> None:
    client = XTwitterAPI()
    post = client.fetch_latest_post("csgocasescom")
    print(post)


if __name__ == "__main__":
    main()
