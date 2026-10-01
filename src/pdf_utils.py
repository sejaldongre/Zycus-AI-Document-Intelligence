from pathlib import Path
import pymupdf


def render_pdf_pages(pdf_path: str, output_dir: str):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    document = pymupdf.open(pdf_path)

    image_paths = []

    for page_number, page in enumerate(document):
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

        image_path = output_dir / f"page_{page_number + 1}.png"

        pixmap.save(image_path)

        image_paths.append(image_path)

    document.close()

    return image_paths

if __name__ == "__main__":
    pdf = "candidate_kit/documents/INV-01.pdf"
    output = "output/rendered/INV-01"

    images = render_pdf_pages(pdf, output)

    for image in images:
        print(image)