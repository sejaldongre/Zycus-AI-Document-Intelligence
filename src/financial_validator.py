from math import isclose


class FinancialValidator:
    """
    Validates the mathematical consistency of extracted
    invoice information.

    This validator does not invent or correct values.

    It only checks whether the supplied values are
    internally consistent.
    """

    DEFAULT_TOLERANCE = 0.02

    def __init__(self, tolerance=None):
        self.tolerance = (
            tolerance
            if tolerance is not None
            else self.DEFAULT_TOLERANCE
        )

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def approximately_equal(
        self,
        actual,
        expected
    ):
        """
        Compare monetary values using a small tolerance.

        Small differences can occur because of rounding.
        """

        if actual is None or expected is None:
            return False

        return isclose(
            float(actual),
            float(expected),
            abs_tol=self.tolerance,
            rel_tol=0,
        )

    # ---------------------------------------------------------
    # Line-item validation
    # ---------------------------------------------------------

    def validate_line_item(self, item):
        """
        Validate:

            quantity × unit_price = total

        after considering line-level discount if present.
        """

        quantity = item.get("quantity")
        unit_price = item.get("unit_price")
        total = item.get("total")

        if (
            quantity is None
            or unit_price is None
            or total is None
        ):
            return {
                "valid": False,
                "reason": "Missing quantity, unit price, or total.",
            }

        expected_total = (
            float(quantity)
            * float(unit_price)
        )

        discount = item.get("discount")

        if discount is not None:
            expected_total -= float(discount)

        valid = self.approximately_equal(
            total,
            expected_total
        )

        return {
            "valid": valid,
            "expected_total": round(
                expected_total,
                2
            ),
            "actual_total": round(
                float(total),
                2
            ),
            "difference": round(
                float(total) - expected_total,
                2
            ),
            "reason": (
                "Line total is mathematically consistent."
                if valid
                else "Line total does not match quantity × unit price."
            ),
        }

    # ---------------------------------------------------------
    # All line items
    # ---------------------------------------------------------

    def validate_line_items(
        self,
        line_items
    ):
        """
        Validate every extracted line item.
        """

        results = []

        for index, item in enumerate(
            line_items or [],
            start=1
        ):

            result = self.validate_line_item(
                item
            )

            result["line_number"] = index

            results.append(result)

        return results

    # ---------------------------------------------------------
    # Subtotal validation
    # ---------------------------------------------------------

    def validate_subtotal(
        self,
        line_items,
        subtotal
    ):
        """
        Check whether the subtotal equals the sum
        of the extracted line totals.
        """

        if subtotal is None:
            return {
                "checked": False,
                "valid": None,
                "reason": "Subtotal was not extracted.",
            }

        if not line_items:
            return {
                "checked": False,
                "valid": None,
                "reason": "No line items available.",
            }

        line_total_sum = sum(
            float(item.get("total", 0))
            for item in line_items
            if item.get("total") is not None
        )

        valid = self.approximately_equal(
            subtotal,
            line_total_sum
        )

        return {
            "checked": True,
            "valid": valid,
            "expected_subtotal": round(
                line_total_sum,
                2
            ),
            "actual_subtotal": round(
                float(subtotal),
                2
            ),
            "difference": round(
                float(subtotal) - line_total_sum,
                2
            ),
        }

    # ---------------------------------------------------------
    # Gross total validation
    # ---------------------------------------------------------

    def validate_gross_total(
        self,
        subtotal,
        total_tax,
        gross_total,
        discount_amount=0,
        freight_charges=0,
        insurance_charges=0,
        extra_charges=0,
        excise_duties=0,
        withholding_amount=0,
    ):
        """
        Perform a basic financial consistency check.

        Conceptually:

        gross =
            subtotal
            - discounts
            + freight
            + insurance
            + extra charges
            + excise duties
            + taxes

        Withholding is treated separately because it generally
        reduces the amount paid rather than increasing gross.
        """

        if subtotal is None:
            return {
                "checked": False,
                "valid": None,
                "reason": "Subtotal is unavailable.",
            }

        if gross_total is None:
            return {
                "checked": False,
                "valid": None,
                "reason": "Gross total is unavailable.",
            }

        subtotal = float(subtotal)

        total_tax = (
            float(total_tax)
            if total_tax is not None
            else 0
        )

        discount_amount = (
            float(discount_amount)
            if discount_amount is not None
            else 0
        )

        freight_charges = (
            float(freight_charges)
            if freight_charges is not None
            else 0
        )

        insurance_charges = (
            float(insurance_charges)
            if insurance_charges is not None
            else 0
        )

        extra_charges = (
            float(extra_charges)
            if extra_charges is not None
            else 0
        )

        excise_duties = (
            float(excise_duties)
            if excise_duties is not None
            else 0
        )

        withholding_amount = (
            float(withholding_amount)
            if withholding_amount is not None
            else 0
        )

        expected_gross = (
            subtotal
            - discount_amount
            + freight_charges
            + insurance_charges
            + extra_charges
            + excise_duties
            + total_tax
        )

        expected_payment = (
            expected_gross
            - withholding_amount
        )

        gross_valid = self.approximately_equal(
            gross_total,
            expected_gross
        )

        return {
            "checked": True,
            "gross_valid": gross_valid,
            "expected_gross": round(
                expected_gross,
                2
            ),
            "actual_gross": round(
                float(gross_total),
                2
            ),
            "gross_difference": round(
                float(gross_total)
                - expected_gross,
                2
            ),
            "expected_payment_after_withholding": round(
                expected_payment,
                2
            ),
        }

    # ---------------------------------------------------------
    # Complete validation
    # ---------------------------------------------------------

    def validate(
        self,
        invoice_data
    ):
        """
        Run all available financial checks.
        """

        line_items = invoice_data.get(
            "line_items",
            []
        )

        subtotal = invoice_data.get(
            "subtotal"
        )

        gross_total = invoice_data.get(
            "gross_total"
        )

        total_tax = invoice_data.get(
            "total_tax_amount"
        )

        line_results = self.validate_line_items(
            line_items
        )

        subtotal_result = self.validate_subtotal(
            line_items,
            subtotal
        )

        gross_result = self.validate_gross_total(
            subtotal=subtotal,
            total_tax=total_tax,
            gross_total=gross_total,
            discount_amount=invoice_data.get(
                "discount_amount",
                0
            ),
            freight_charges=invoice_data.get(
                "freight_charges",
                0
            ),
            insurance_charges=invoice_data.get(
                "insurance_charges",
                0
            ),
            extra_charges=invoice_data.get(
                "extra_charges",
                0
            ),
            excise_duties=invoice_data.get(
                "excise_duties",
                0
            ),
            withholding_amount=invoice_data.get(
                "withholding_amount",
                0
            ),
        )

        all_line_items_valid = all(
            result["valid"]
            for result in line_results
            if result["valid"] is not None
        )

        return {
            "line_items": line_results,
            "all_line_items_valid": all_line_items_valid,
            "subtotal_check": subtotal_result,
            "gross_check": gross_result,
        }


# ============================================================
# TEST
# ============================================================

def main():

    validator = FinancialValidator()

    invoice = {
        "subtotal": 438.00,
        "total_tax_amount": 0.00,
        "gross_total": 438.00,
        "line_items": [
            {
                "description":
                    "Project management - November",
                "quantity": 4,
                "unit_price": 73,
                "total": 292,
            },
            {
                "description":
                    "Project management - December",
                "quantity": 2,
                "unit_price": 73,
                "total": 146,
            },
        ],
    }

    result = validator.validate(
        invoice
    )

    print("\n===== FINANCIAL VALIDATION =====\n")

    print("Line item checks:")

    for item in result["line_items"]:
        print(
            f"Line {item['line_number']}: "
            f"{item['valid']} | "
            f"Expected = {item['expected_total']} | "
            f"Actual = {item['actual_total']}"
        )

    print("\nAll line items valid:")
    print(
        result["all_line_items_valid"]
    )

    print("\nSubtotal check:")
    print(
        result["subtotal_check"]
    )

    print("\nGross check:")
    print(
        result["gross_check"]
    )


if __name__ == "__main__":
    main()
