import json
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ERP_PATH = PROJECT_ROOT / "candidate_kit" / "erp.py"


TOLERANCE = 0.02


def load_erp_book():
    spec = importlib.util.spec_from_file_location(
        "candidate_erp",
        ERP_PATH
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load ERP module from: {ERP_PATH}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.erp_book


erp_book = load_erp_book()


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_payable(payable):
    expected_gross = payable.get("gross_total")

    if expected_gross is None:
        return {
            "valid": False,
            "reason": "gross_total is missing",
            "erp_gross": None,
        }

    try:
        expected_gross = float(expected_gross)

    except (TypeError, ValueError):
        return {
            "valid": False,
            "reason": "gross_total is not numeric",
            "erp_gross": None,
        }

    try:
        result = erp_book(payable)

        erp_gross = float(
            result.get(
                "will_book_gross",
                0
            )
        )

    except Exception as exc:

        return {
            "valid": False,
            "reason": f"ERP error: {exc}",
            "erp_gross": None,
        }

    difference = abs(
        erp_gross - expected_gross
    )

    return {
        "valid": difference <= TOLERANCE,

        "reason": (
            "ERP gross matches gross_total"
            if difference <= TOLERANCE
            else (
                f"ERP gross differs by "
                f"{difference:.2f}"
            )
        ),

        "erp_gross": erp_gross,

        "document_gross":
            expected_gross,

        "difference":
            difference,

        "currency":
            result.get(
                "currency",
                ""
        ),
    }


def main():

    print("=" * 70)
    print("ZYCUS ERP VALIDATION")
    print("=" * 70)

    json_files = sorted(
        OUTPUT_DIR.glob("*.json")
    )

    if not json_files:

        print(
            "No JSON files found in output/"
        )

        return

    total_payables = 0
    passed = 0
    failed = 0

    print(
        f"\nFound {len(json_files)} JSON files.\n"
    )

    for json_path in json_files:

        data = load_json(
            json_path
        )

        payables = data.get(
            "payables",
            []
        )

        if not payables:

            print(
                f"{json_path.name:<18} "
                f"NO PAYABLE"
            )

            continue

        for index, payable in enumerate(
            payables,
            start=1
        ):

            total_payables += 1

            result = validate_payable(
                payable
            )

            if result["valid"]:

                passed += 1

                print(
                    f"{json_path.name:<18} "
                    f"payable[{index}] "
                    f"PASS  "
                    f"ERP="
                    f"{result['erp_gross']:.2f} "
                    f"Document="
                    f"{result['document_gross']:.2f} "
                    f"{result['currency']}"
                )

            else:

                failed += 1

                print(
                    f"{json_path.name:<18} "
                    f"payable[{index}] "
                    f"FAIL  "
                    f"{result['reason']}"
                )

                if result.get(
                    "erp_gross"
                ) is not None:

                    print(
                        f"  ERP gross     : "
                        f"{result['erp_gross']:.2f}"
                    )

                    print(
                        f"  Document gross: "
                        f"{result['document_gross']:.2f}"
                    )

                    print(
                        f"  Difference    : "
                        f"{result['difference']:.2f}"
                    )

    print(
        "\n" + "=" * 70
    )

    print(
        "ERP VALIDATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Total payables : "
        f"{total_payables}"
    )

    print(
        f"ERP PASS       : "
        f"{passed}"
    )

    print(
        f"ERP FAIL       : "
        f"{failed}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()
