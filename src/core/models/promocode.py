import easyocr
import requests
import numpy as np
import undetected_chromedriver as uc

from PIL import Image
from io import BytesIO
from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from config import URL, DEBUG
from utils.driver import load_cookies
from core.repositories import PromocodeRepository


@dataclass
class Promocode:
    post_url: str
    image_url: str

    _code: str = field(default=None, repr=False)
    _image: Image.Image = field(default=None, repr=False)
    _driver: uc.Chrome = field(default=None, repr=False)
    _repository: PromocodeRepository = field(default_factory=PromocodeRepository, repr=False)

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
            image = self.image

            # Crop the image to focus on the code area
            width, height = image.size
            image = image.crop((width * 0.1, height * 0.62, width * 0.9, height * 0.8))
            image = image.convert("RGB")

            reader = easyocr.Reader(["en"], gpu=True)
            result = reader.readtext(np.array(image), allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", detail=0)

            if result:
                self._code = result[0].strip()

        return self._code

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
