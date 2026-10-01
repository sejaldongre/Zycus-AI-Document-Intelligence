import json
import re
from pathlib import Path


MASTER_DATA_DIR = Path("candidate_kit/master_data")


class SupplierMatcher:
    """
    Resolves supplier information against the supplied
    supplier master data.

    Matching strategy:
    1. Exact VAT ID match
    2. Normalized supplier-name match
    3. Otherwise return an unmatched supplier
    """

    def __init__(self):
        supplier_file = MASTER_DATA_DIR / "suppliers.json"

        with open(
            supplier_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        self.suppliers = data["suppliers"]

    @staticmethod
    def normalize_text(value: str) -> str:
        """
        Normalize text for safer comparison.

        Example:
            "Phocus Direct Communication GmbH"
            →
            "phocusdirectcommunicationgmbh"
        """

        if not value:
            return ""

        value = value.lower()

        value = re.sub(
            r"[^a-z0-9]",
            "",
            value
        )

        return value

    @staticmethod
    def normalize_vat(value: str) -> str:
        """
        Normalize VAT IDs by removing spaces and punctuation.
        """

        if not value:
            return ""

        return re.sub(
            r"[^a-zA-Z0-9]",
            "",
            value
        ).upper()

    def match(
        self,
        supplier_name: str | None = None,
        vat_id: str | None = None
    ) -> dict:

        normalized_name = self.normalize_text(
            supplier_name
        )

        normalized_vat = self.normalize_vat(
            vat_id
        )

        # --------------------------------------------------
        # 1. VAT ID matching
        # --------------------------------------------------

        if normalized_vat:

            for supplier in self.suppliers:

                master_vat = self.normalize_vat(
                    supplier.get("vat_id", "")
                )

                if (
                    master_vat
                    and master_vat == normalized_vat
                ):

                    return {
                        "matched": True,
                        "match_type": "vat_id",
                        "supplier": supplier,
                    }

        # --------------------------------------------------
        # 2. Exact normalized name matching
        # --------------------------------------------------

        if normalized_name:

            for supplier in self.suppliers:

                master_name = self.normalize_text(
                    supplier.get("name", "")
                )

                if (
                    master_name
                    and master_name == normalized_name
                ):

                    return {
                        "matched": True,
                        "match_type": "name",
                        "supplier": supplier,
                    }

        # --------------------------------------------------
        # 3. No reliable match
        # --------------------------------------------------

        return {
            "matched": False,
            "match_type": None,
            "supplier": None,
        }


def main():

    matcher = SupplierMatcher()

    # Test using the supplier extracted from INV-01.
    result = matcher.match(
        supplier_name="Phocus Direct Communication GmbH",
        vat_id="DE209177122"
    )
    print("\n===== SUPPLIER MATCH RESULT =====\n")

    print(f"Matched: {result['matched']}")
    print(f"Match type: {result['match_type']}")

    if result["supplier"]:
        print("\nMatched supplier:")

        for key, value in result["supplier"].items():
            print(f"{key}: {value}")

    else:
        print("\nNo supplier master-data match found.")


if __name__ == "__main__":
    main()