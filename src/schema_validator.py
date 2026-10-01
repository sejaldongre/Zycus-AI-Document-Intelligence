import json
from pathlib import Path


class AutoDraftSchemaValidator:
    """
    Basic structural validator for the Zycus AutoDraft format.
    """

    REQUIRED_TOP_LEVEL_FIELDS = {
        "file",
        "payables",
        "declined",
    }

    REQUIRED_PAYABLE_FIELDS = {
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
        "subtotal",
        "total_tax_amount",
        "taxes",
        "line_items",
    }

    REQUIRED_SUPPLIER_FIELDS = {
        "name",
        "supplier_id",
        "address",
        "vat_id",
    }

    REQUIRED_BUYER_FIELDS = {
        "company_code",
        "business_unit_code",
        "location_code",
    }

    def validate(self, data: dict):

        errors = []

        # --------------------------------------------------
        # Top-level structure
        # --------------------------------------------------

        missing = (
            self.REQUIRED_TOP_LEVEL_FIELDS
            - set(data.keys())
        )

        for field in sorted(missing):

            errors.append(
                f"Missing top-level field: {field}"
            )

        # --------------------------------------------------
        # Payables
        # --------------------------------------------------

        payables = data.get(
            "payables",
            []
        )

        if not isinstance(payables, list):

            errors.append(
                "payables must be a list"
            )

            payables = []

        for index, payable in enumerate(
            payables,
            start=1
        ):

            if not isinstance(
                payable,
                dict
            ):

                errors.append(
                    f"Payable {index} must be an object"
                )

                continue

            missing_payable = (
                self.REQUIRED_PAYABLE_FIELDS
                - set(payable.keys())
            )

            for field in sorted(
                missing_payable
            ):

                errors.append(
                    f"Payable {index}: "
                    f"missing field: {field}"
                )

            # --------------------------------------------------
            # Supplier
            # --------------------------------------------------

            supplier = payable.get(
                "supplier"
            )

            if not isinstance(
                supplier,
                dict
            ):

                errors.append(
                    f"Payable {index}: "
                    "supplier must be an object"
                )

            else:

                missing_supplier = (
                    self.REQUIRED_SUPPLIER_FIELDS
                    - set(supplier.keys())
                )

                for field in sorted(
                    missing_supplier
                ):

                    errors.append(
                        f"Payable {index}: "
                        f"supplier missing field: {field}"
                    )

            # --------------------------------------------------
            # Buyer
            # --------------------------------------------------

            buyer = payable.get(
                "buyer"
            )

            if not isinstance(
                buyer,
                dict
            ):

                errors.append(
                    f"Payable {index}: "
                    "buyer must be an object"
                )

            else:

                missing_buyer = (
                    self.REQUIRED_BUYER_FIELDS
                    - set(buyer.keys())
                )

                for field in sorted(
                    missing_buyer
                ):

                    errors.append(
                        f"Payable {index}: "
                        f"buyer missing field: {field}"
                    )

            # --------------------------------------------------
            # Taxes
            # --------------------------------------------------

            if not isinstance(
                payable.get("taxes"),
                list
            ):

                errors.append(
                    f"Payable {index}: "
                    "taxes must be a list"
                )

            # --------------------------------------------------
            # Line items
            # --------------------------------------------------

            if not isinstance(
                payable.get("line_items"),
                list
            ):

                errors.append(
                    f"Payable {index}: "
                    "line_items must be a list"
                )

        # --------------------------------------------------
        # Declined
        # --------------------------------------------------

        declined = data.get(
            "declined",
            []
        )

        if not isinstance(
            declined,
            list
        ):

            errors.append(
                "declined must be a list"
            )

        else:

            for index, item in enumerate(
                declined,
                start=1
            ):

                if not isinstance(
                    item,
                    dict
                ):

                    errors.append(
                        f"Declined item {index} "
                        "must be an object"
                    )

                    continue

                if "doc_type" not in item:

                    errors.append(
                        f"Declined item {index}: "
                        "missing doc_type"
                    )

                if "reason" not in item:

                    errors.append(
                        f"Declined item {index}: "
                        "missing reason"
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }


def main():

    json_path = Path(
        "output/test_autodraft/INV-01.json"
    )

    with open(
        json_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    validator = AutoDraftSchemaValidator()

    result = validator.validate(
        data
    )

    print(
        "\n===== AUTODRAFT SCHEMA VALIDATION =====\n"
    )

    print(
        f"Valid: {result['valid']}"
    )

    if result["errors"]:

        print("\nErrors:")

        for error in result["errors"]:

            print(
                f"  - {error}"
            )

    else:

        print(
            "\nNo structural errors found."
        )


if __name__ == "__main__":
    main()
