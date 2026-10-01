import re


class DocumentClassifier:
    """
    Evidence-based document classifier.

    The classifier combines multiple document signals rather
    than relying on a single keyword.

    This is still a deterministic baseline. The purpose is to
    create a transparent and testable classification layer.
    """

    CREDIT_MEMO_TERMS = [
        "credit memo",
        "credit note",
        "creditnote",
        "gutschrift",
    ]

    DEBIT_NOTE_TERMS = [
        "debit note",
        "debit memo",
        "debitnote",
        "belastungsanzeige",
    ]

    REMINDER_TERMS = [
        "mahnung",
        "payment reminder",
        "dunning",
        "past due",
        "overdue payment",
        "outstanding payment",
        "restbetrag",
    ]

    INVOICE_TERMS = [
        "invoice",
        "tax invoice",
        "rechnung",
        "arve",
        "factura",
    ]

    def normalize_text(self, text: str) -> str:
        """
        Normalize extracted document text.
        """

        if not text:
            return ""

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def contains_any(
        self,
        text: str,
        terms: list[str]
    ) -> list[str]:

        matches = []

        for term in terms:

            if term in text:
                matches.append(term)

        return matches

    def classify(
        self,
        text_lines: list[str]
    ) -> dict:
        """
        Classify a document using multiple independent signals.
        """

        text = self.normalize_text(
            "\n".join(text_lines)
        )

        evidence = []

        # --------------------------------------------------
        # Strong document-type signals
        # --------------------------------------------------

        credit_matches = self.contains_any(
            text,
            self.CREDIT_MEMO_TERMS
        )

        debit_matches = self.contains_any(
            text,
            self.DEBIT_NOTE_TERMS
        )

        reminder_matches = self.contains_any(
            text,
            self.REMINDER_TERMS
        )

        invoice_matches = self.contains_any(
            text,
            self.INVOICE_TERMS
        )

        # --------------------------------------------------
        # Financial/document structure signals
        # --------------------------------------------------

        has_invoice_number = bool(
            re.search(
                r"\b(invoice\s*(number|no|#)|"
                r"rechnungsnummer|"
                r"invoice\s*id)\b",
                text
            )
        )

        has_invoice_date = bool(
            re.search(
                r"\b(invoice\s*date|"
                r"rechnungsdatum|"
                r"date)\b",
                text
            )
        )

        has_due_date = bool(
            re.search(
                r"\b(due\s*date|"
                r"fällig|"
                r"payment\s*due)\b",
                text
            )
        )

        has_total = bool(
            re.search(
                r"\b(total|"
                r"gross\s*total|"
                r"amount\s*due|"
                r"balance\s*due|"
                r"endbetrag|"
                r"gesamtsumme)\b",
                text
            )
        )

        has_supplier_buyer_language = bool(
            re.search(
                r"\b("
                r"supplier|vendor|seller|"
                r"bill\s*to|buyer|customer|"
                r"ship\s*to"
                r")\b",
                text
            )
        )

        # --------------------------------------------------
        # Credit memo
        # --------------------------------------------------

        if credit_matches:

            evidence.extend(
                f"credit:{term}"
                for term in credit_matches
            )

            return {
                "doc_type": "CREDIT_MEMO",
                "is_payable_candidate": True,
                "confidence": "high",
                "evidence": evidence,
            }

        # --------------------------------------------------
        # Debit note
        # --------------------------------------------------

        if debit_matches:

            evidence.extend(
                f"debit:{term}"
                for term in debit_matches
            )

            return {
                "doc_type": "DEBIT_NOTE",
                "is_payable_candidate": True,
                "confidence": "high",
                "evidence": evidence,
            }

        # --------------------------------------------------
        # Payment reminder
        # --------------------------------------------------

        if reminder_matches:

            evidence.extend(
                f"reminder:{term}"
                for term in reminder_matches
            )

            return {
                "doc_type": "PAYMENT_REMINDER",
                "is_payable_candidate": False,
                "confidence": "high",
                "evidence": evidence,
            }

        # --------------------------------------------------
        # Invoice scoring
        # --------------------------------------------------

        invoice_score = 0

        for term in invoice_matches:

            evidence.append(
                f"invoice:{term}"
            )

            invoice_score += 2

        if has_invoice_number:

            evidence.append(
                "structure:invoice_number"
            )

            invoice_score += 2

        if has_invoice_date:

            evidence.append(
                "structure:invoice_date"
            )

            invoice_score += 1

        if has_due_date:

            evidence.append(
                "structure:due_date"
            )

            invoice_score += 1

        if has_total:

            evidence.append(
                "structure:total"
            )

            invoice_score += 2

        if has_supplier_buyer_language:

            evidence.append(
                "structure:parties"
            )

            invoice_score += 1

        # --------------------------------------------------
        # Payable invoice threshold
        # --------------------------------------------------

        if invoice_score >= 5:

            return {
                "doc_type": "INVOICE",
                "is_payable_candidate": True,
                "confidence": "high",
                "score": invoice_score,
                "evidence": evidence,
            }

        # --------------------------------------------------
        # Unknown
        # --------------------------------------------------

        return {
            "doc_type": "UNKNOWN",
            "is_payable_candidate": False,
            "confidence": "low",
            "score": invoice_score,
            "evidence": evidence,
        }


def main():

    classifier = DocumentClassifier()

    # --------------------------------------------------
    # Test 1: Invoice
    # --------------------------------------------------

    invoice_text = [
        "Tax Invoice",
        "Invoice Number: 7363916",
        "Invoice Date: 30.06.2026",
        "Customer: ABC Corporation",
        "Currency: SGD",
        "Total amount in SGD",
        "Terms of payment: 90 days net",
        "Due Date: 28.09.2026",
    ]

    print("\n===== TEST 1: INVOICE =====")

    print(
        classifier.classify(
            invoice_text
        )
    )

    # --------------------------------------------------
    # Test 2: Payment reminder
    # --------------------------------------------------

    reminder_text = [
        "Mahnung",
        "Rechnung",
        "Restbetrag",
        "Bitte überweisen Sie den Betrag",
        "Fällig",
    ]

    print(
        "\n===== TEST 2: PAYMENT REMINDER ====="
    )

    print(
        classifier.classify(
            reminder_text
        )
    )

    # --------------------------------------------------
    # Test 3: Credit memo
    # --------------------------------------------------

    credit_text = [
        "Credit Note",
        "Credit Memo Number: CM-1001",
        "Invoice Date: 10.06.2026",
        "Total: EUR 250.00",
    ]

    print(
        "\n===== TEST 3: CREDIT MEMO ====="
    )

    print(
        classifier.classify(
            credit_text
        )
    )

    # --------------------------------------------------
    # Test 4: Debit note
    # --------------------------------------------------

    debit_text = [
        "Debit Note",
        "Debit Note Number: DN-1001",
        "Amount Due: EUR 500.00",
    ]

    print(
        "\n===== TEST 4: DEBIT NOTE ====="
    )

    print(
        classifier.classify(
            debit_text
        )
    )


if __name__ == "__main__":
    main()
