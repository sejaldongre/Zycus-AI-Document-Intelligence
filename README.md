# Zycus AI Document Intelligence

## Bookable Payable — Autodraft Generation System

An automated document-intelligence pipeline that converts supplier PDF documents into structured accounting autodrafts for downstream ERP booking.

The system determines whether a document represents a bookable payable, extracts the financial information required by the AutoDraft schema, resolves available master-data references, and generates one JSON output for each input PDF.

---

## 1. Objective

The system processes supplier documents that may contain:

- Invoices
- Credit memos
- Payment reminders
- Other non-payable documents
- Multiple pages
- Multiple line items
- Different currencies
- Different document layouts
- Native PDF text
- Scanned or image-based pages requiring OCR

For every PDF, the system determines:

1. What type of document it is.
2. Whether it contains a bookable payable.
3. What financial components are stated on the document.
4. Which master-data values can be matched.
5. How the information should be represented in the AutoDraft schema.

Documents that are not payables are placed in `declined[]` rather than being forced into `payables[]`.

---

## 2. System Pipeline

```text
Supplier PDF
     |
     v
Native PDF Text Extraction
     |
     |-- sufficient text --> continue
     |
     |-- insufficient text
     v
OCR Fallback
     |
     v
Document Classification
     |
     v
Information Extraction
     |
     v
Master-Data Resolution
     |
     v
Financial Validation
     |
     v
AutoDraft Generation
     |
     v
output/X.json
```

The generated AutoDraft preserves the financial structure present on the document.

For example:

- Line-level taxes remain at line level.
- Header-level taxes remain at header level.
- Quantities and net unit prices remain separate.
- Discounts remain separate from prices.
- Charges and levies remain decomposed.
- Master-data codes are populated only when a genuine match exists.

---

## 3. Project Structure

```text
Zycus AI Document Intelligence/
|
├── candidate_kit/
│   ├── documents/
│   ├── master_data/
│   ├── AUTODRAFT_SCHEMA.md
│   ├── README.md
│   ├── erp.py
│   ├── example_check.py
│   └── sample_autodraft.json
|
├── src/
│   ├── autodraft_builder.py
│   ├── document_classifier.py
│   ├── document_extractor.py
│   ├── financial_validator.py
│   ├── information_extractor.py
│   ├── master_data.py
│   ├── master_data_resolver.py
│   ├── ocr.py
│   ├── pdf_utils.py
│   ├── pipeline.py
│   ├── run_all.py
│   └── validate_all.py
|
├── output/
├── check_erp.py
├── DESIGN.md
└── README.md
```

---

## 4. Requirements

### Python

The project runs inside the project's Python virtual environment.

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

### OCR

The system uses Tesseract OCR when native PDF text extraction is insufficient.

The OCR executable is configured in:

```text
src/ocr.py
```

The current configuration expects:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## 5. Running the System

From the project root:

```text
C:\Sejal Projects\Zycus AI Document Intelligence
```

run the following command:

```powershell
python -m src.run_all
```

This is the main command for the project.

The command automatically:

1. Reads all PDFs from:

```text
candidate_kit/documents/
```

2. Processes each document.

3. Determines whether the document contains a payable.

4. Extracts the required information.

5. Resolves available master-data references.

6. Generates one JSON file per PDF.

7. Writes the results to:

```text
output/
```

For example:

```text
candidate_kit/documents/INV-01.pdf
```

produces:

```text
output/INV-01.json
```

---

## 6. Output Format

Each input PDF produces one JSON file.

The output follows the required structure:

```json
{
  "file": "X.pdf",
  "payables": [],
  "declined": []
}
```

### Payable document

A payable is represented inside:

```json
"payables": [
  {
    "invoice_type": "INVOICE",
    "currency": "EUR",
    "gross_total": "...",
    "line_items": [],
    "taxes": []
  }
]
```

A credit memo uses the same AutoDraft schema with:

```json
"invoice_type": "CREDIT_MEMO"
```

and its monetary values are represented using the document's positive magnitudes.

### Non-payable document

A document that is determined not to be a payable is represented using:

```json
"payables": [],
"declined": [
  {
    "doc_type": "...",
    "reason": "..."
  }
]
```

A document can contain zero, one, or multiple payable records.

---

## 7. Document Extraction

The extraction layer first attempts to obtain native text from the PDF.

If the available native text is insufficient, the system:

1. Renders the PDF pages.
2. Runs OCR on the rendered pages.
3. Cleans the extracted text.
4. Passes the resulting document text to the downstream pipeline.

This allows the system to process both digitally generated PDFs and image-based documents.

---

## 8. Document Classification

Before generating an AutoDraft, the system classifies the document.

The classifier uses evidence present in the document, including document terminology and financial/document signals.

Examples include:

- Invoice terminology
- Credit memo terminology
- Payment reminder terminology
- Invoice numbers
- Dates
- Payment-related information

Documents identified as non-payables are not forced into the payable schema.

Instead, they are written to `declined[]` with the detected document type and reason.

---

## 9. Information Extraction

For payable candidates, the extraction layer identifies information required by the AutoDraft schema, including where available:

- Invoice number
- Invoice date
- Due date
- Invoice type
- Currency
- Supplier information
- Buyer information
- Payment terms
- Purchase order information
- Gross total
- Subtotal
- Taxes
- Discounts
- Freight and other charges
- Line items

The system attempts to preserve the structure stated by the source document rather than creating balancing values that are not present on the document.

---

## 10. Master-Data Resolution

The project includes reference data for:

- Suppliers
- Tax information
- Buyer organisation information
- Payment terms
- Purchase orders

Document values are matched against the supplied master data.

An internal code is emitted only when a genuine match exists.

If no valid match exists, the corresponding internal code is left blank rather than being guessed.

---

## 11. Financial Validation

The system performs financial consistency checks on extracted components.

The validation considers relationships between:

- Quantities
- Net unit prices
- Line totals
- Discounts
- Taxes
- Freight
- Insurance
- Other charges
- Excise duties
- Subtotals
- Gross totals

The financial validator is used as a diagnostic layer while the supplied ERP recomputation provides the final accounting check.

---

## 12. ERP Validation

The challenge provides `candidate_kit/erp.py` as the ERP recomputation used to determine the gross amount that would be booked from a generated payable.

The project includes:

```text
check_erp.py
```

as a validation utility.

Run:

```powershell
python check_erp.py
```

The final generated outputs currently produce:

```text
Total payables : 24
ERP PASS       : 24
ERP FAIL       : 0
Pass rate      : 100.00%
```

The ERP validation is performed from the generated payable components rather than simply comparing a copied document total.

---

## 13. Structural Validation

The project also includes:

```text
src/validate_all.py
```

Run:

```powershell
python src/validate_all.py
```

The current generated outputs produce:

```text
Valid   : 42
Invalid : 0
```

---

## 14. Current Validation Results

The current implementation has been tested on the supplied 42 PDF documents.

| Validation           | Result |
| -------------------- | -----: |
| Documents processed  |     42 |
| Successful documents |     42 |
| Failed documents     |      0 |
| Valid JSON outputs   |     42 |
| Invalid JSON outputs |      0 |
| Payable records      |     24 |
| ERP payable passes   |     24 |
| ERP payable failures |      0 |
| ERP pass rate        |   100% |

---

## 15. Design Principles

The implementation follows these principles:

1. **Evidence over assumptions**  
   Values are extracted from the document rather than invented.

2. **Structure over total-only matching**  
   Quantities, prices, discounts, taxes and charges are preserved according to their placement in the document.

3. **Conservative master-data matching**  
   Internal codes are emitted only when supported by a genuine master-data match.

4. **Payable vs. non-payable separation**  
   Documents that are not bookable payables are placed in `declined[]`.

5. **OCR fallback**  
   Image-based documents are processed when native PDF text is insufficient.

6. **ERP verification**  
   Generated payable components are checked against the supplied ERP recomputation.

---

## 16. Design Documentation

The reasoning behind the extraction strategy, handling of unseen documents, and exceptional document cases is documented separately in:

```text
DESIGN.md
```

This document explains how the system approaches generalisation beyond the supplied examples.

---

## 17. Output Location

After running:

```powershell
python -m src.run_all
```

the generated files are available under:

```text
output/
```

with one JSON file corresponding to each input PDF:

```text
output/
├── DU-02.json
├── DU-03.json
├── ...
└── INV-37.json
```

The output directory is created automatically if it does not already exist.
