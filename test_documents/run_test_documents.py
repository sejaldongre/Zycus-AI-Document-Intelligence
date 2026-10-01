from pathlib import Path
import json

from src.pipeline import InvoicePipeline
from src.autodraft_builder import AutoDraftBuilder

test_dir = Path("test_documents")
result_dir = test_dir / "results"
result_dir.mkdir(exist_ok=True)

pipeline = InvoicePipeline()
builder = AutoDraftBuilder()

files = sorted(test_dir.glob("*.pdf"))

print("=" * 70)
print("TESTING TEST DOCUMENTS")
print("=" * 70)
print(f"Found {len(files)} PDF files")
print()

for pdf_file in files:
    print(f"Processing: {pdf_file.name}")

    try:
        result = builder.build(str(pdf_file))

        output_file = result_dir / f"{pdf_file.stem}.json"
        output_file.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8"
        )

        print(f"  Payables : {len(result.get('payables', []))}")
        print(f"  Declined : {len(result.get('declined', []))}")
        print(f"  Saved    : {output_file}")
        print()

    except Exception as e:
        print(f"  ERROR: {e}")
        print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
