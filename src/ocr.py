from pathlib import Path
import os
import shutil

import pytesseract
from PIL import Image


class OCRProcessor:

    def __init__(self, language="eng"):
        self.language = language

        # Prefer an explicitly configured Tesseract executable.
        # This works on both local Windows and cloud Linux environments.
        configured_path = os.getenv("TESSERACT_CMD")

        if configured_path:
            self.tesseract_path = configured_path
        else:
            # Use PATH-based Tesseract when available (e.g. Render/Linux).
            path_tesseract = shutil.which("tesseract")

            if path_tesseract:
                self.tesseract_path = path_tesseract
            else:
                # Keep the existing Windows installation as a fallback.
                self.tesseract_path = (
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                )

        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

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
