import easyocr
import requests
import numpy as np
from PIL import Image
from io import BytesIO


def read_promocode_from_image_url(url: str) -> str:
    """Read an image from a URL and return the text content."""

    response = requests.get(url)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))

    # Crop the image to focus on the code area
    width, height = image.size
    image = image.crop((width * 0.1, height * 0.62, width * 0.9, height * 0.8))
    image = image.convert("RGB")

    reader = easyocr.Reader(["en"], gpu=True)
    result = reader.readtext(np.array(image), allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", detail=0)

    return result[0].strip()
