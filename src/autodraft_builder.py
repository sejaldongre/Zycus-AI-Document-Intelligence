
from pathlib import Path
import json

from src.pipeline import InvoicePipeline


class AutoDraftBuilder:
    def __init__(self):
        self.pipeline = InvoicePipeline()

    def build(self, pdf_path: str):
        """
        Process one supplier PDF and return the AutoDraft result
        as a Python dictionary.
        """

        result = self.pipeline.process(pdf_path)

        classification = result["classification"]
        extracted = result["extracted"]
        master_data = result["master_data"]

        file_name = Path(pdf_path).name

        # =========================================================
        # NON-PAYABLE DOCUMENT
        # =========================================================

        if not classification.get(
            "is_payable_candidate",
            False
        ):

            doc_type = (
                classification.get("doc_type")
                or "UNKNOWN"
            )

            confidence = (
                classification.get("confidence")
                or "low"
            )

            evidence = (
                classification.get("evidence")
                or []
            )

            if evidence:

                evidence_text = ", ".join(
                    str(item)
                    for item in evidence
                )

                reason = (
                    f"Document classified as {doc_type} "
                    f"based on detected evidence: "
                    f"{evidence_text}."
                )

            else:

                reason = (
                    f"Document classified as {doc_type} "
                    f"with {confidence} confidence "
                    f"and is not a payable."
                )

            return {
                "file": file_name,
                "payables": [],
                "declined": [
                    {
                        "doc_type": doc_type,
                        "reason": reason
                    }
                ]
            }

        # =========================================================
        # SUPPLIER MASTER DATA
        # =========================================================

        supplier_match = (
            master_data.get("supplier")
            or {}
        )

        matched_supplier = (
            supplier_match.get("supplier")
        )

        # The pipeline preserves the supplier's document value in
        # extracted["supplier"] after master-data resolution. Prefer that
        # value so an unmatched supplier name is not lost.
        extracted_supplier = (
            extracted.get("supplier")
            if isinstance(extracted.get("supplier"), dict)
            else {}
        )

        document_supplier_name = (
            extracted_supplier.get("name")
            or extracted.get("supplier_name")
        )

        document_supplier_vat = (
            extracted_supplier.get("vat_id")
            or extracted.get("vat_id")
        )

        if matched_supplier:

            supplier = {
                "name": document_supplier_name,
                "supplier_id": matched_supplier.get(
                    "supplier_id",
                    matched_supplier.get("id", "")
                ),
                "address": matched_supplier.get(
                    "address",
                    ""
                ) or extracted_supplier.get("address", ""),
                "vat_id": document_supplier_vat
            }

        else:

            supplier = {
                "name": document_supplier_name,
                "supplier_id": "",
                "address": extracted_supplier.get("address", ""),
                "vat_id": document_supplier_vat
            }

        # =========================================================
        # PAYMENT TERM MASTER DATA
        # =========================================================

        payment_term_match = (
            master_data.get("payment_term")
            or {}
        )

        payment_term = (
            payment_term_match.get(
                "payment_term"
            )
        )

        payment_term_id = ""

        if payment_term:

            payment_term_id = payment_term.get(
                "payment_term_id",
                payment_term.get("id", "")
            )

        # =========================================================
        # PURCHASE ORDER MASTER DATA
        # =========================================================

        purchase_order_match = (
            master_data.get("purchase_order")
            or {}
        )

        purchase_order = (
            purchase_order_match.get(
                "purchase_order"
            )
        )

        po_id = ""

        po_number = extracted.get(
            "po_number"
        )

        if purchase_order:

            po_id = purchase_order.get(
                "po_id",
                purchase_order.get("id", "")
            )

            if not po_number:

                po_number = purchase_order.get(
                    "po_number"
                )

        # =========================================================
        # TAX MASTER DATA
        # =========================================================

        taxes = []

        for tax in extracted.get(
            "taxes",
            []
        ) or []:

            if not isinstance(
                tax,
                dict
            ):
                continue

            tax_entry = {
                "tax_type": tax.get(
                    "tax_type",
                    ""
                ),
                "tax_name": tax.get(
                    "tax_name",
                    ""
                ),
                "tax_rate": tax.get(
                    "tax_rate",
                    ""
                ),
                "tax_amount": tax.get(
                    "tax_amount",
                    ""
                ),
                "tax_type_code": ""
            }

            for resolved_tax in master_data.get(
                "taxes",
                []
            ) or []:

                if not isinstance(
                    resolved_tax,
                    dict
                ):
                    continue

                document_tax = (
                    resolved_tax.get(
                        "document_tax"
                    )
                    or {}
                )

                master_match = (
                    resolved_tax.get(
                        "master_match"
                    )
                    or {}
                )

                if document_tax == tax:

                    matched_tax = (
                        master_match.get(
                            "tax"
                        )
                    )

                    if matched_tax:

                        tax_entry[
                            "tax_type_code"
                        ] = matched_tax.get(
                            "tax_type_code",
                            matched_tax.get(
                                "code",
                                ""
                            )
                        )

            taxes.append(
                tax_entry
            )

        # =========================================================
        # LINE ITEMS
        # =========================================================

        line_items = []

        for item in extracted.get(
            "line_items",
            []
        ) or []:

            if not isinstance(
                item,
                dict
            ):
                continue

            line = {
                "description": item.get(
                    "description",
                    ""
                ),
                "item_type": item.get(
                    "item_type",
                    "SERVICE"
                ),
                "uom": item.get(
                    "uom",
                    ""
                ),
                "quantity": item.get(
                    "quantity",
                    ""
                ),
                "unit_price": item.get(
                    "unit_price",
                    ""
                ),
                "total": item.get(
                    "total",
                    ""
                ),
                "discount": item.get(
                    "discount",
                    ""
                ),
                "discount_percentage": item.get(
                    "discount_percentage",
                    ""
                ),
                "tax_rate": item.get(
                    "tax_rate",
                    ""
                ),
                "tax_amount": item.get(
                    "tax_amount",
                    ""
                ),
                "taxes": item.get(
                    "taxes",
                    []
                ) or []
            }

            line_items.append(
                line
            )

        # =========================================================
        # PAYABLE OBJECT
        # =========================================================

        payable = {
            "invoice_number": extracted.get(
                "invoice_number"
            ),
            "invoice_date": extracted.get(
                "invoice_date"
            ),
            "due_date": extracted.get(
                "due_date"
            ),
            "invoice_type": extracted.get(
                "invoice_type",
                "INVOICE"
            ),
            "currency": extracted.get(
                "currency",
                ""
            ),
            "supplier": supplier,
            "buyer": {
                "company_code": extracted.get(
                    "company_code",
                    ""
                ),
                "business_unit_code": extracted.get(
                    "business_unit_code",
                    ""
                ),
                "location_code": extracted.get(
                    "location_code",
                    ""
                )
            },
            "payment_term_id": payment_term_id,
            "po_number": po_number,
            "po_id": po_id,
            "gross_total": extracted.get(
                "gross_total",
                ""
            ),
            "subtotal": extracted.get(
                "subtotal",
                ""
            ),
            "total_tax_amount": extracted.get(
                "total_tax_amount",
                ""
            ),
            "discount_amount": extracted.get(
                "discount_amount",
                ""
            ),
            "freight_charges": extracted.get(
                "freight_charges",
                ""
            ),
            "insurance_charges": extracted.get(
                "insurance_charges",
                ""
            ),
            "extra_charges": extracted.get(
                "extra_charges",
                ""
            ),
            "excise_duties": extracted.get(
                "excise_duties",
                ""
            ),
            "taxes": taxes,
            "line_items": line_items
        }

        return {
            "file": file_name,
            "payables": [
                payable
            ],
            "declined": []
        }

    # =============================================================
    # SAVE
    # =============================================================

    def save(
        self,
        pdf_path: str,
        output_path: str
    ):
        """
        Process the PDF, save its JSON output, and return
        the generated result dictionary.

        This matches the interface expected by src.run_all.py.
        """

        result = self.build(
            pdf_path
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                indent=2,
                ensure_ascii=False
            )

        return result


def build_output(
    pdf_path: str,
    output_dir: str
):
    """
    Convenience function for processing one PDF.
    """

    builder = AutoDraftBuilder()

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir
        / f"{Path(pdf_path).stem}.json"
    )

    return builder.save(
        pdf_path,
        str(output_path)
    )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Build AutoDraft JSON "
            "from a supplier PDF."
        )
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the supplier PDF"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help=(
            "Directory where the JSON "
            "should be written"
        )
    )

    args = parser.parse_args()

    result = build_output(
        args.pdf_path,
        args.output_dir
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
