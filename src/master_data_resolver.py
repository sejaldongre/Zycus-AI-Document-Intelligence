import json
import re
from pathlib import Path


class MasterDataResolver:

    def __init__(self, master_data_dir="candidate_kit/master_data"):

        self.master_data_dir = Path(master_data_dir)

        self.suppliers = self._load_json(
            "suppliers.json"
        )

        self.payment_terms = self._load_json(
            "payment_terms.json"
        )

        self.po_master = self._load_json(
            "po_master.json"
        )

        self.tax_master = self._load_json(
            "tax_master.json"
        )

        self.chart_of_books = self._load_json(
            "chart_of_books.json"
        )

    # =========================================================
    # LOAD JSON
    # =========================================================

    def _load_json(self, filename):

        path = self.master_data_dir / filename

        if not path.exists():
            return []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            # Handle common wrapper formats
            for key in [
                "data",
                "records",
                "items",
                "suppliers",
                "payment_terms",
                "purchase_orders",
                "taxes",
                "companies",
            ]:

                if key in data and isinstance(
                    data[key],
                    list
                ):
                    return data[key]

        return []

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def normalize_text(self, value):

        if value is None:
            return ""

        value = str(value).lower().strip()

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        value = re.sub(
            r"[.,]",
            "",
            value
        )

        return value

    def normalize_code(self, value):

        if value is None:
            return ""

        return re.sub(
            r"[^a-zA-Z0-9]",
            "",
            str(value)
        ).lower()

    def normalize_number(self, value):

        if value is None:
            return ""

        return re.sub(
            r"[^0-9]",
            "",
            str(value)
        )

    # =========================================================
    # SUPPLIER
    # =========================================================

    def resolve_supplier(
        self,
        supplier_name=None,
        vat_id=None
    ):

        normalized_name = self.normalize_text(
            supplier_name
        )

        normalized_vat = self.normalize_code(
            vat_id
        )

        # -----------------------------------------------------
        # 1. VAT ID exact match
        # -----------------------------------------------------

        if normalized_vat:

            for supplier in self.suppliers:

                master_vat = self.normalize_code(
                    supplier.get("vat_id")
                    or supplier.get("vat")
                    or supplier.get("tax_id")
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

        # -----------------------------------------------------
        # 2. Exact normalized supplier name
        # -----------------------------------------------------

        if normalized_name:

            for supplier in self.suppliers:

                master_name = self.normalize_text(
                    supplier.get("name")
                    or supplier.get("supplier_name")
                    or supplier.get("vendor_name")
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

        # -----------------------------------------------------
        # No match
        # -----------------------------------------------------

        return {
            "matched": False,
            "match_type": None,
            "supplier": None,
        }

    # =========================================================
    # PAYMENT TERM
    # =========================================================

    def resolve_payment_term(
        self,
        payment_term
    ):

        if not payment_term:
            return {
                "matched": False,
                "payment_term": None,
            }

        normalized_input = self.normalize_text(
            payment_term
        )

        # -----------------------------------------------------
        # Exact text / alias matching
        # -----------------------------------------------------

        for term in self.payment_terms:

            term_texts = []

            for key in [
                "text",
                "name",
                "description",
                "payment_term",
                "term",
            ]:

                value = term.get(key)

                if value:
                    term_texts.append(value)

            aliases = term.get(
                "text_aliases",
                []
            )

            if isinstance(aliases, list):
                term_texts.extend(aliases)

            elif aliases:
                term_texts.append(aliases)

            for candidate in term_texts:

                normalized_candidate = self.normalize_text(
                    candidate
                )

                if not normalized_candidate:
                    continue

                if (
                    normalized_input
                    == normalized_candidate
                ):

                    return {
                        "matched": True,
                        "payment_term": term,
                    }

        # -----------------------------------------------------
        # Normalize common "90 days net" style values
        # -----------------------------------------------------

        days_match = re.search(
            r"(\d+)\s*days?",
            normalized_input
        )

        if days_match:

            requested_days = int(
                days_match.group(1)
            )

            for term in self.payment_terms:

                master_days = term.get(
                    "days"
                )

                if master_days is None:
                    continue

                try:
                    master_days = int(
                        master_days
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    continue

                if master_days == requested_days:

                    return {
                        "matched": True,
                        "payment_term": term,
                    }

        return {
            "matched": False,
            "payment_term": None,
        }

    # =========================================================
    # PURCHASE ORDER
    # =========================================================

    def resolve_purchase_order(
        self,
        po_number
    ):

        if not po_number:
            return {
                "matched": False,
                "purchase_order": None,
            }

        normalized_po = self.normalize_code(
            po_number
        )

        for po in self.po_master:

            candidates = [
                po.get("po_number"),
                po.get("number"),
                po.get("po_id"),
                po.get("id"),
            ]

            for candidate in candidates:

                if (
                    candidate
                    and self.normalize_code(candidate)
                    == normalized_po
                ):

                    return {
                        "matched": True,
                        "purchase_order": po,
                    }

        return {
            "matched": False,
            "purchase_order": None,
        }

    # =========================================================
    # TAX
    # =========================================================

    def resolve_tax(
        self,
        tax_name=None,
        tax_rate=None
    ):

        normalized_name = self.normalize_text(
            tax_name
        )

        requested_rate = None

        if tax_rate is not None:

            try:
                requested_rate = float(
                    tax_rate
                )
            except (
                TypeError,
                ValueError
            ):
                requested_rate = None

        for tax in self.tax_master:

            master_name = self.normalize_text(
                tax.get("tax_name")
                or tax.get("name")
                or tax.get("description")
            )

            master_rate = tax.get(
                "tax_rate"
            )

            if master_rate is None:
                master_rate = tax.get(
                    "rate"
                )

            try:

                if master_rate is not None:
                    master_rate = float(
                        master_rate
                    )

            except (
                TypeError,
                ValueError
            ):

                master_rate = None

            name_match = (
                normalized_name
                and master_name
                and normalized_name == master_name
            )

            rate_match = (
                requested_rate is not None
                and master_rate is not None
                and abs(
                    requested_rate - master_rate
                ) < 0.0001
            )

            if name_match and rate_match:

                return {
                    "matched": True,
                    "tax": tax,
                }

            if name_match and requested_rate is None:

                return {
                    "matched": True,
                    "tax": tax,
                }

        return {
            "matched": False,
            "tax": None,
        }

    # =========================================================
    # BUYER / CHART OF BOOKS
    # =========================================================

    def resolve_buyer(
        self,
        company_name=None,
        company_code=None,
        business_unit_code=None,
        location_code=None
    ):

        requested_codes = [
            self.normalize_code(company_code),
            self.normalize_code(business_unit_code),
            self.normalize_code(location_code),
        ]

        requested_codes = [
            value
            for value in requested_codes
            if value
        ]

        # Search all records recursively
        records = []

        def collect_records(value):

            if isinstance(value, list):

                for item in value:
                    collect_records(item)

            elif isinstance(value, dict):

                records.append(value)

                for child in value.values():
                    collect_records(child)

        collect_records(
            self.chart_of_books
        )

        # Exact code match
        if requested_codes:

            for record in records:

                record_codes = []

                for key in [
                    "company_code",
                    "business_unit_code",
                    "location_code",
                    "code",
                    "id",
                ]:

                    value = record.get(key)

                    if value:
                        record_codes.append(
                            self.normalize_code(value)
                        )

                if all(
                    requested in record_codes
                    for requested in requested_codes
                ):

                    return {
                        "matched": True,
                        "buyer": record,
                    }

        # Company-name match
        if company_name:

            normalized_company = self.normalize_text(
                company_name
            )

            for record in records:

                names = [
                    record.get("company_name"),
                    record.get("name"),
                    record.get("company"),
                ]

                for name in names:

                    if (
                        name
                        and self.normalize_text(name)
                        == normalized_company
                    ):

                        return {
                            "matched": True,
                            "buyer": record,
                        }

        return {
            "matched": False,
            "buyer": None,
        }
