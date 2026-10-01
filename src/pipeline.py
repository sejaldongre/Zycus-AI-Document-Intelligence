from src.document_extractor import DocumentExtractor
from src.document_classifier import DocumentClassifier
from src.information_extractor import InvoiceInformationExtractor
from src.master_data_resolver import MasterDataResolver
from src.financial_validator import FinancialValidator


class InvoicePipeline:

    def __init__(self):

        self.document_extractor = DocumentExtractor()

        self.classifier = DocumentClassifier()

        self.information_extractor = (
            InvoiceInformationExtractor()
        )

        self.master_data_resolver = (
            MasterDataResolver()
        )

        self.validator = FinancialValidator()

    # =========================================================
    # PROCESS DOCUMENT
    # =========================================================

    def process(self, pdf_path: str):

        # -----------------------------------------------------
        # 1. Extract document text
        # -----------------------------------------------------

        document = (
            self.document_extractor.extract_from_pdf(
                pdf_path
            )
        )

        # -----------------------------------------------------
        # 2. Classify document
        # -----------------------------------------------------

        classification = (
            self.classifier.classify(
                document["text"]
            )
        )

        # -----------------------------------------------------
        # 3. Extract information
        # -----------------------------------------------------

        extracted = (
            self.information_extractor.extract(
                document["text"]
            )
        )

        # -----------------------------------------------------
        # 4. Resolve supplier
        # -----------------------------------------------------

        supplier_match = (
            self.master_data_resolver.resolve_supplier(
                supplier_name=extracted.get(
                    "supplier_name"
                ),
                vat_id=extracted.get(
                    "vat_id"
                )
            )
        )

        # -----------------------------------------------------
        # 5. Resolve payment term
        # -----------------------------------------------------

        payment_term_match = (
            self.master_data_resolver.resolve_payment_term(
                extracted.get(
                    "payment_term"
                )
            )
        )

        # -----------------------------------------------------
        # 6. Resolve purchase order
        # -----------------------------------------------------

        purchase_order_match = (
            self.master_data_resolver.resolve_purchase_order(
                extracted.get(
                    "po_number"
                )
            )
        )

        # -----------------------------------------------------
        # 7. Resolve taxes
        # -----------------------------------------------------

        resolved_taxes = []

        for tax in extracted.get(
            "taxes",
            []
        ):

            tax_match = (
                self.master_data_resolver.resolve_tax(
                    tax_name=tax.get(
                        "tax_name"
                    ),
                    tax_rate=tax.get(
                        "tax_rate"
                    )
                )
            )

            resolved_taxes.append(
                {
                    "document_tax": tax,
                    "master_match": tax_match,
                }
            )

        # -----------------------------------------------------
        # 8. Build supplier object
        # -----------------------------------------------------

        matched_supplier = (
            supplier_match.get(
                "supplier"
            )
        )

        if matched_supplier:

            supplier = {

                "name": extracted.get(
                    "supplier_name"
                ),

                "supplier_id": (
                    matched_supplier.get(
                        "supplier_id",
                        matched_supplier.get(
                            "id",
                            ""
                        )
                    )
                ),

                "vat_id": extracted.get(
                    "vat_id"
                ),

                "address": matched_supplier.get(
                    "address",
                    ""
                ),
            }

        else:

            supplier = {

                "name": extracted.get(
                    "supplier_name"
                ),

                "supplier_id": "",

                "vat_id": extracted.get(
                    "vat_id"
                ),

                "address": "",
            }

        extracted["supplier"] = supplier

        # Remove temporary field
        extracted.pop(
            "supplier_name",
            None
        )

        # -----------------------------------------------------
        # 9. Financial validation
        # -----------------------------------------------------

        validation = (
            self.validator.validate(
                extracted
            )
        )

        # -----------------------------------------------------
        # 10. Return complete pipeline result
        # -----------------------------------------------------

        return {

            "document": document,

            "classification": classification,

            "extracted": extracted,

            "master_data": {

                "supplier": supplier_match,

                "payment_term": payment_term_match,

                "purchase_order": (
                    purchase_order_match
                ),

                "taxes": resolved_taxes,
            },

            "validation": validation,
        }


if __name__ == "__main__":

    import json

    pipeline = InvoicePipeline()

    result = pipeline.process(
        "candidate_kit/documents/DU-05.pdf"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
