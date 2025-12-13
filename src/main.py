from common import Promocode, QuestionApp


def main() -> None:
    # app = QuestionApp()
    # reply = app.run()
    # print(reply)

    promocode = Promocode('YOUR_PROMOCODE_HERE', 'https://your-post-url.com')
    promocode.store()


if __name__ == "__main__":
    main()