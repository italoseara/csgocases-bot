# CSGOCases Bot

This project is a bot designed to interact with the CSGOCases platform, scraping promocodes from social media posts and automatically redeeming them on the CSGOCases website. The bot features a Textual User Interface (TUI) for easy monitoring and control.

> [!CAUTION]
> Using bots to interact with websites may violate their terms of service. Use at your own risk, the author is not responsible for any misuse or damages caused by this software.

> [!WARNING] 
> CSGOCases is a gambling platform. I do not endorse or encourage gambling. This bot is not a gambling tool, but rather a utility to automate the process of redeeming promocodes. Please gamble responsibly and be aware of the risks involved.

> [!IMPORTANT]
> I am not affiliated with CSGOCases or any of the social media platforms used for scraping promocodes. This project is for educational purposes only.

## Features

- Scrapes promocodes from specified social media platforms (Twitter, Discord, Facebook and Instagram).
- Automatically redeems promocodes on the CSGOCases website.
- Textual User Interface (TUI) for monitoring bot activity and status.
- Configurable settings for scraping intervals and social media credentials.

## Running the Bot

1. Clone the repository:

   ```bash
   git clone https://github.com/italoseara/csgocases-bot
   cd csgocases-bot
   ```

2. Use `uv` to run the bot:

   ```bash
   uv run src/main.py
   ```

3. Follow the on-screen instructions in the TUI to configure and start the bot.

## Configuration

The bot can be configured through the TUI. You can set your social media credentials, scraping intervals, and other settings directly within the interface.

To find the `X Auth Token` and `X CSRF Token` for X (formerly Twitter), you can use your browser's developer tools while logged into your account. Look for `auth_token` and `ct0` cookies respectively in the storage section.

To find the `Discord Auth Token`, you can use your browser's developer tools while logged into your Discord account. Look for `Authorization` header in the network requests.

## Dependencies

- Python 3.12+
- Textual
- Selenium
- Other dependencies listed in `pyproject.toml`

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.