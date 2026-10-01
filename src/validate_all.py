from pathlib import Path
import json
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PATHS
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# VALIDATION
# ============================================================

def validate_output(data):

    errors = []

    if not isinstance(data, dict):
        errors.append(
            "Output must be a JSON object."
        )
        return errors

    if "file" not in data:
        errors.append(
            "Missing required field: file"
        )

    if "payables" not in data:
        errors.append(
            "Missing required field: payables"
        )
    elif not isinstance(data["payables"], list):
        errors.append(
            "payables must be a list."
        )

    if "declined" not in data:
        errors.append(
            "Missing required field: declined"
        )
    elif not isinstance(data["declined"], list):
        errors.append(
            "declined must be a list."
        )

    for index, payable in enumerate(
        data.get("payables", [])
    ):

        if not isinstance(payable, dict):

            errors.append(
                f"payables[{index}] must be an object."
            )

            continue

        required_fields = [
            "invoice_number",
            "invoice_date",
            "due_date",
            "invoice_type",
            "currency",
            "supplier",
            "buyer",
            "payment_term_id",
            "po_number",
            "po_id",
            "gross_total",
            "total_tax_amount",
            "discount_amount",
            "freight_charges",
            "insurance_charges",
            "extra_charges",
            "excise_duties",
            "taxes",
            "line_items",
        ]

        for field in required_fields:

            if field not in payable:

                errors.append(
                    f"payables[{index}] missing field: {field}"
                )

        if "supplier" in payable:

            if not isinstance(
                payable["supplier"],
                dict
            ):

                errors.append(
                    f"payables[{index}].supplier must be an object."
                )

            else:

                for field in [
                    "name",
                    "supplier_id",
                    "address",
                    "vat_id",
                ]:

                    if field not in payable["supplier"]:

                        errors.append(
                            f"payables[{index}].supplier missing field: {field}"
                        )

        if "buyer" in payable:

            if not isinstance(
                payable["buyer"],
                dict
            ):

                errors.append(
                    f"payables[{index}].buyer must be an object."
                )

            else:

                for field in [
                    "company_code",
                    "business_unit_code",
                    "location_code",
                ]:

                    if field not in payable["buyer"]:

                        errors.append(
                            f"payables[{index}].buyer missing field: {field}"
                        )

        if "taxes" in payable:

            if not isinstance(
                payable["taxes"],
                list
            ):

                errors.append(
                    f"payables[{index}].taxes must be a list."
                )

        if "line_items" in payable:

            if not isinstance(
                payable["line_items"],
                list
            ):

                errors.append(
                    f"payables[{index}].line_items must be a list."
                )

            else:

                for line_index, line in enumerate(
                    payable["line_items"]
                ):

                    if not isinstance(line, dict):

                        errors.append(
                            f"payables[{index}].line_items[{line_index}] must be an object."
                        )

                        continue

                    line_required_fields = [
                        "description",
                        "item_type",
                        "uom",
                        "quantity",
                        "unit_price",
                        "total",
                        "discount",
                        "discount_percentage",
                        "tax_rate",
                        "tax_amount",
                        "taxes",
                    ]

                    for field in line_required_fields:

                        if field not in line:

                            errors.append(
                                f"payables[{index}].line_items[{line_index}] missing field: {field}"
                            )

    for index, declined in enumerate(
        data.get("declined", [])
    ):

        if not isinstance(
            declined,
            dict
        ):

            errors.append(
                f"declined[{index}] must be an object."
            )

            continue

        if "doc_type" not in declined:

            errors.append(
                f"declined[{index}] missing field: doc_type"
            )

        if "reason" not in declined:

            errors.append(
                f"declined[{index}] missing field: reason"
            )

    return errors


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("ZYCUS AUTODRAFT STRUCTURAL VALIDATION")
    print("=" * 70)

    json_files = sorted(
        OUTPUT_DIR.glob("*.json")
    )

    print(
        f"\nFound {len(json_files)} JSON files."
    )

    valid_count = 0
    invalid_count = 0

    for json_path in json_files:

        print(
            f"\nChecking: {json_path.name}"
        )

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            errors = validate_output(data)

            if not errors:

                print("  VALID")

                valid_count += 1

            else:

                print("  INVALID")

                for error in errors:

                    print(
                        f"    - {error}"
                    )

                invalid_count += 1

        except Exception as exc:

            print(
                f"  ERROR: {type(exc).__name__}: {exc}"
            )

            invalid_count += 1

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

    print(
        f"Valid   : {valid_count}"
    )

    print(
        f"Invalid : {invalid_count}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
