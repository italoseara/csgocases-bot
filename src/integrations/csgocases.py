import os
import pickle
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from config import DEBUG, USER_AGENT


class CSGOCasesAPI:
    URL = "https://csgocases.com/"
    COOKIES_PATH = "data/cookies.pkl"

    def __init__(self) -> None:
        """Client for interacting with the CSGOCases website."""

        self.driver = self._create_driver(headless=not DEBUG)
        self._is_logged_in = None
        self.username = None

    def _create_driver(self, headless: bool = True) -> uc.Chrome:
        """Create a Chrome driver with anti-detection options."""

        options = uc.ChromeOptions()

        if headless:
            # Use the new headless mode which is harder to detect
            options.add_argument("--headless=new")

        # Anti-detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument(f"--user-agent={USER_AGENT}")

        # Disable automation flags
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")

        return uc.Chrome(options=options, use_subprocess=False)

    def quit(self) -> None:
        """Quit the webdriver session."""

        self.driver.quit()

    def is_logged_in(self) -> bool:
        """Check if the user is logged in."""

        if self._is_logged_in is not None:
            return self._is_logged_in

        if not os.path.exists(self.COOKIES_PATH):
            return False

        self.driver.get(self.URL)
        self._load_cookies()

        try:
            username = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".nick-limited")))

            self.username = username.text
            self._is_logged_in = True
        except:
            self._is_logged_in = False

        return self._is_logged_in

    def login(self) -> None:
        """Open the login page for the user to log in manually."""

        self.driver.quit()
        self.driver = self._create_driver(headless=False)
        self.driver.get(self.URL)

        WebDriverWait(self.driver, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".nick-limited")))

        self._save_cookies()
        self.driver.quit()

        self.driver = self._create_driver(headless=not DEBUG)

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

    def _save_cookies(self) -> None:
        """Save cookies to a file."""

        with open(self.COOKIES_PATH, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)

    def _load_cookies(self) -> None:
        """Load cookies from a file."""

        with open(self.COOKIES_PATH, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
