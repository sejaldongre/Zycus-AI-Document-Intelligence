from pathlib import Path

import pytesseract
from PIL import Image


class OCRProcessor:

    def __init__(self, language="eng"):

        self.language = language

        # Windows Tesseract installation
        self.tesseract_path = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        pytesseract.pytesseract.tesseract_cmd = (
            self.tesseract_path
        )

    def extract_text(self, image_path: str) -> list[str]:

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image,
            lang=self.language
        )

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        return lines
