from common import Promocode, QuestionApp


def main() -> None:
    # app = QuestionApp()
    # reply = app.run()
    # print(reply)

    promocode = Promocode(
        "https://x.com/csgocasescom/status/1998825144442089497/photo/1",
        "https://pbs.twimg.com/media/G71A30pXMAA88Uv?format=jpg&name=medium",
    )
    print(promocode.code)


if __name__ == "__main__":
    main()
