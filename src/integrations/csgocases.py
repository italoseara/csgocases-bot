import os
import pickle
import undetected_chromedriver as uc

from typing import Self
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from config import DEBUG


class CSGOCasesAPI:
    URL = "https://csgocases.com/"
    COOKIES_PATH = "data/cookies.pkl"

    def __init__(self) -> None:
        """Client for interacting with the CSGOCases website."""

        self.driver = None

    def __enter__(self) -> Self:
        """Initialize the web driver."""

        self.driver = uc.Chrome(headless=not DEBUG, use_subprocess=False)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Quit the web driver."""

        self.driver.quit()

    def claim_promocode(self, promocode: str) -> None:
        """Claim a promocode on the website."""

        try:
            self.driver.get(self.URL)
            self._load_cookies()

            wait = WebDriverWait(self.driver, 10)
            wallet_funds = wait.until(EC.element_to_be_clickable((By.ID, "walletFunds")))
            wallet_funds.click()

            promocode_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.tabs > a:nth-child(7)")))
            promocode_tab.click()

            promocode_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.promocode input")))
            promocode_input.send_keys(promocode)

            claim_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.promocode button")))
            claim_button.click()

            # Click on Cloudflare challenge when it appears
            cloudflare_iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#recaptcha-promocode > div"))
            ).shadow_root.find_element(By.CSS_SELECTOR, "iframe")

            self.driver.switch_to.frame(cloudflare_iframe)

            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).shadow_root
            wait.until(lambda d: body.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]'))  # Wait for checkbox to load

            self.driver.switch_to.default_content()

            actions = ActionChains(self.driver)
            actions.move_to_element(promocode_input)
            actions.click()
            actions.send_keys("\t")  # Press tab to focus on the checkbox
            actions.send_keys(" ")  # Press space to click the checkbox
            actions.perform()

            # Wait for the toast notification
            toast = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ui-notification")))
            status = "success" if "success" in toast.get_attribute("class") else "error"
            message = toast.find_element(By.CSS_SELECTOR, "div.message").text

            return {"status": status, "message": message}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.driver.close()

    def _save_cookies(self) -> None:
        """Save cookies to a file."""

        with open(self.COOKIES_PATH, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)

    def _load_cookies(self) -> None:
        """Load cookies from a file."""

        try:
            if not os.path.exists(os.path.dirname(self.COOKIES_PATH)):
                os.makedirs(os.path.dirname(self.COOKIES_PATH))

            with open(self.COOKIES_PATH, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
        except FileNotFoundError:
            print(f"Cookie file '{self.COOKIES_PATH}' not found. No cookies loaded.")
