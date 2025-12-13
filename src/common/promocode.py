import os
import psycopg2
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from util.driver import load_cookies
from config import URL, DEBUG


load_dotenv()


class Promocode:
    def __init__(self, post_url: str) -> None:
        self.post_url = post_url
        self.code = None

        self._driver = None

    def connect_db(self) -> psycopg2.connection:
        """Connect to the PostgreSQL database."""

        USER = os.getenv("DB_USER")
        PASSWORD = os.getenv("DB_PASSWORD")
        HOST = os.getenv("DB_HOST")
        PORT = os.getenv("DB_PORT")
        DBNAME = os.getenv("DB_NAME")

        return psycopg2.connect(user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME)

    def store(self) -> None:
        """Store cookies in a remote database."""

        if self.exists():
            print("Promocode already exists in the database.")
            return

        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    insert_query = """
                    INSERT INTO promocodes (code, post_url)
                    VALUES (%s, %s)
                    """

                    cursor.execute(insert_query, (self.code, self.post_url))
                    conn.commit()
            print("Promocode stored successfully.")
        except Exception as e:
            print(f"Database error: {e}")

    def exists(self) -> bool:
        """Check if a promocode exists by post URL."""

        try:
            with self.connect_db() as conn:
                with conn.cursor() as cursor:
                    select_query = """
                    SELECT EXISTS(
                        SELECT 1 FROM promocodes WHERE post_url = %s
                    )
                    """

                    cursor.execute(select_query, (self.post_url,))
                    exists = cursor.fetchone()[0]
            return exists
        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get(self) -> str:
        """Use an LLM (Gemini) to read and set the promocode."""

        raise NotImplementedError("LLM integration not implemented.")

    def claim(self) -> dict:
        """Claim a promocode on the website."""

        try:
            self._driver = uc.Chrome(headless=not DEBUG, use_subprocess=False)
            self._driver.get(URL)
            load_cookies(self._driver)

            wait = WebDriverWait(self._driver, 10)
            wallet_funds = wait.until(EC.element_to_be_clickable((By.ID, "walletFunds")))
            wallet_funds.click()

            promocode_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.tabs > a:nth-child(7)")))
            promocode_tab.click()

            promocode_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.promocode input")))
            promocode_input.send_keys(self.code)

            claim_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.promocode button")))
            claim_button.click()

            # Click on Cloudflare challenge when it appears
            cloudflare_iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#recaptcha-promocode > div"))
            ).shadow_root.find_element(By.CSS_SELECTOR, "iframe")

            self._driver.switch_to.frame(cloudflare_iframe)

            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).shadow_root
            wait.until(
                lambda d: body.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            )  # Wait for checkbox to load

            self._driver.switch_to.default_content()

            actions = ActionChains(self._driver)
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
            self._driver.quit()


if __name__ == "__main__":
    promocode = Promocode("YOUR_PROMOCODE_HERE")
    promocode.store()
    # result = promocode.claim()
    # print(result)
