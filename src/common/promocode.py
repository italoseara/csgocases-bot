import os
import psycopg2
import requests
import undetected_chromedriver as uc
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from google import genai
from google.genai import types
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from util.driver import load_cookies
from config import URL, DEBUG


load_dotenv()


class Promocode:
    post_url: str
    image_url: str

    _code: str
    _image: Image.Image
    _driver: uc.Chrome

    def __init__(self, post_url: str, image_url: str = None) -> None:
        self.post_url = post_url
        self.image_url = image_url

        self._code = None
        self._image = None
        self._driver = None

    @property
    def image(self) -> Image.Image:
        """Get the promocode image."""

        if self._image is None and self.image_url:
            response = requests.get(self.image_url)
            self._image = Image.open(BytesIO(response.content))

        return self._image

    @property
    def code(self) -> str:
        """Get the promocode text."""

        if self._code is None and self.image_url:
            try:
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                response = client.models.list()
                print(response.page)
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_uri(file_uri=self.image_url, mime_type="image/jpeg"),
                        (
                            "**System / Instruction Prompt for the Agent:**\n"
                            "You are an AI assistant that extracts promo codes from images.\n"
                            "\n"
                            "* Your only job is to detect and return the promo code text exactly as it appears in the image.\n"
                            "* Promo codes may contain letters, numbers, or both.\n"
                            "* Do not include extra words, symbols, or formatting. Return only the code itself.\n"
                            '* The promo code is bellow the word "PROMOCODE" and above a "like" or "heart" symbol.\n'
                            '* The word "PROMOCODE" is NOT a promo code.\n'
                            "* Output nothing else beyond the code.\n"
                            "\n"
                            "**Expected Output Examples:**\n"
                            "\n"
                            "* If the promo code in the image is 'FB12', respond with:\n"
                            "  FB12\n"
                            "* If the promo code in the image is 'DC10', respond with:\n"
                            "  DC10\n"
                        ),
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=500,
                        top_p=0.8,
                    ),
                )

                self._code = response.text.strip()
            except Exception as e:
                print(f"Error extracting promocode: {e}")

        return self._code

    def connect_db(self) -> psycopg2.extensions.connection:
        """Connect to the PostgreSQL database."""

        return psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        )

    def store(self) -> None:
        """Store promocode in a remote database."""

        if not self.code:
            print("No promocode to store.")
            return

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

    def claim(self) -> dict:
        """Claim a promocode on the website."""

        if not self.code:
            return {"status": "error", "message": "Code not available."}

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
