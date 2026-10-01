from src.autodraft_builder import AutoDraftBuilder
from pathlib import Path
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Make the project root available to Python
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT PROJECT CODE
# ============================================================


# ============================================================
# PATHS
# ============================================================

DOCUMENTS_DIR = PROJECT_ROOT / "candidate_kit" / "documents"
OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# MAIN BATCH PROCESS
# ============================================================

def main():

    print("=" * 70)
    print("ZYCUS AI DOCUMENT INTELLIGENCE")
    print("BATCH AUTODRAFT PROCESSOR")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    builder = AutoDraftBuilder()

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    print(
        f"\nFound {len(pdf_files)} PDF documents."
    )

    print(
        f"Documents folder: {DOCUMENTS_DIR}"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )

    print("\n" + "=" * 70)

    successful = 0
    failed = 0

    for pdf_path in pdf_files:

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.json"

        print(
            f"\nProcessing: {pdf_path.name}"
        )

        try:

            result = builder.save(
                str(pdf_path),
                str(output_path)
            )

            payables = len(
                result.get("payables", [])
            )

            declined = len(
                result.get("declined", [])
            )

            print(
                f"  Payables : {payables}"
            )

            print(
                f"  Declined : {declined}"
            )

            print(
                f"  Saved    : {output_path}"
            )

            successful += 1

        except Exception as exc:

            failed += 1

            print(
                f"  FAILED   : {type(exc).__name__}: {exc}"
            )

    print("\n" + "=" * 70)
    print("BATCH COMPLETE")
    print("=" * 70)

    print(
        f"Successful : {successful}"
    )

    print(
        f"Failed     : {failed}"
    )

    print(
        f"Output     : {OUTPUT_DIR.resolve()}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
