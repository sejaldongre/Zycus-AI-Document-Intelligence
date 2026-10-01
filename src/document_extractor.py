from pathlib import Path

from pypdf import PdfReader

from src.pdf_utils import render_pdf_pages


class DocumentExtractor:
    """
    Hybrid PDF document extractor.

    Strategy:
    1. Try native PDF text extraction first.
    2. If enough usable text exists, use it directly.
    3. Otherwise render the PDF pages and use OCR.

    OCR is initialized lazily so that native PDFs do not
    unnecessarily load the OCR model.
    """

    def __init__(self):
        self.ocr_processor = None

    def _get_ocr_processor(self):
        """
        Initialize OCR only when it is actually required.
        """
        if self.ocr_processor is None:
            from src.ocr import OCRProcessor

            self.ocr_processor = OCRProcessor()

        return self.ocr_processor

    def extract_native_text(self, pdf_path: str) -> list[str]:
        """
        Extract text directly from the PDF.

        Returns:
            list[str]: cleaned text lines.
        """

        reader = PdfReader(pdf_path)

        text_lines = []

        for page in reader.pages:

            page_text = page.extract_text() or ""

            for line in page_text.splitlines():

                line = line.strip()

                if line:
                    text_lines.append(line)

        return text_lines

    def has_usable_text(self, text_lines: list[str]) -> bool:
        """
        Decide whether native PDF extraction produced
        enough text to avoid OCR.
        """

        total_characters = sum(
            len(line)
            for line in text_lines
        )

        return total_characters >= 50

    def extract_from_pdf(self, pdf_path: str) -> dict:
        """
        Extract text from a PDF using the hybrid strategy.
        """

        pdf_path = Path(pdf_path)

        # --------------------------------------------------
        # STEP 1: Try native PDF text extraction
        # --------------------------------------------------

        native_text = self.extract_native_text(
            str(pdf_path)
        )

        if self.has_usable_text(native_text):

            reader = PdfReader(pdf_path)

            return {
                "document": pdf_path.name,
                "pages": len(reader.pages),
                "method": "native_pdf",
                "text": native_text,
            }

        # --------------------------------------------------
        # STEP 2: Fall back to OCR
        # --------------------------------------------------

        print(
            f"[OCR] Native text insufficient for "
            f"{pdf_path.name}. Running OCR..."
        )

        render_dir = (
            Path("output/rendered")
            / pdf_path.stem
        )

        image_paths = render_pdf_pages(
            str(pdf_path),
            str(render_dir)
        )

        ocr_processor = self._get_ocr_processor()

        all_text = []

        for image_path in image_paths:

            page_text = ocr_processor.extract_text(
                str(image_path)
            )

            all_text.extend(page_text)

        return {
            "document": pdf_path.name,
            "pages": len(image_paths),
            "method": "ocr",
            "text": all_text,
        }


def main():

    extractor = DocumentExtractor()

    test_documents = [
        "candidate_kit/documents/INV-31.pdf",
        "candidate_kit/documents/INV-01.pdf",
    ]

    for pdf_path in test_documents:

        print("\n" + "=" * 70)

        result = extractor.extract_from_pdf(
            pdf_path
        )

        print(
            f"Document: {result['document']}"
        )

        print(
            f"Pages: {result['pages']}"
        )

        print(
            f"Method: {result['method']}"
        )

        print("\nExtracted text:")

        for line in result["text"][:20]:
            print(line)


if __name__ == "__main__":
    main()
