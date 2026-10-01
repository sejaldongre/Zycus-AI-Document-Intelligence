import json
from pathlib import Path
from erp import erp_book

results_dir = Path("test_documents/results")
files = sorted(results_dir.glob("*.json"))

print("=" * 70)
print("TEST DOCUMENT ERP VALIDATION")
print("=" * 70)

total = 0
passed = 0
failed = 0

for file in files:
    data = json.loads(file.read_text(encoding="utf-8"))
    payables = data.get("payables", [])

    if not payables:
        print(f"{file.name:<35} NO PAYABLE")
        continue

    for index, payable in enumerate(payables, start=1):
        total += 1

        erp_result = erp_book(payable)
        erp_gross = erp_result["will_book_gross"]
        document_gross = float(payable.get("gross_total") or 0)

        if abs(erp_gross - document_gross) < 0.02:
            passed += 1
            print(
                f"{file.name:<35} payable[{index}] PASS "
                f"ERP={erp_gross:.2f} "
                f"Document={document_gross:.2f} "
                f"{erp_result['currency']}"
            )
        else:
            failed += 1
            print(
                f"{file.name:<35} payable[{index}] FAIL "
                f"ERP={erp_gross:.2f} "
                f"Document={document_gross:.2f}"
            )

print()
print("=" * 70)
print("ERP VALIDATION SUMMARY")
print("=" * 70)
print(f"Total payables : {total}")
print(f"ERP PASS       : {passed}")
print(f"ERP FAIL       : {failed}")

if total:
    print(f"Pass rate      : {(passed / total) * 100:.2f}%")

print("=" * 70)
