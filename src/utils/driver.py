import os
import pickle
from selenium.webdriver.remote.webdriver import WebDriver

from config import COOKIE_PATH


def save_cookies(driver: WebDriver) -> None:
    """Save cookies to a file."""

    with open(COOKIE_PATH, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver: WebDriver) -> None:
    """Load cookies from a file."""

    try:
        if not os.path.exists(os.path.dirname(COOKIE_PATH)):
            os.makedirs(os.path.dirname(COOKIE_PATH))

        with open(COOKIE_PATH, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        print(f"Cookie file '{COOKIE_PATH}' not found. No cookies loaded.")
