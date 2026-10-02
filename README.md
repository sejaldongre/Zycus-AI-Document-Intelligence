# Zycus AI Document Intelligence

## Bookable Payable — AutoDraft Generation System

An automated document-intelligence pipeline that converts supplier PDF documents into structured accounting AutoDrafts for downstream ERP booking.

The system determines whether a document represents a bookable payable, extracts the financial information required by the AutoDraft schema, resolves available master-data references, validates the extracted financial structure, and generates one JSON output for each input PDF.

---

## Live Demo and Source Code

### Live Demo

The Streamlit application is deployed and available here:

**Live Demo:** https://zycus-ai-document-intelligence.onrender.com

### GitHub Repository

The complete source code and project files are available here:

**GitHub:** https://github.com/sejaldongre/Zycus-AI-Document-Intelligence

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
ERP Validation
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
- Documents identified as non-payables are represented in `declined[]`.

---

## 3. Project Structure

```text
Zycus AI Document Intelligence/
|
|-- candidate_kit/
|   |-- documents/
|   |-- master_data/
|   |   |-- README.md
|   |   |-- chart_of_books.json
|   |   |-- payment_terms.json
|   |   |-- po_master.json
|   |   |-- suppliers.json
|   |   `-- tax_master.json
|   |-- AUTODRAFT_SCHEMA.md
|   |-- README.md
|   |-- erp.py
|   |-- example_check.py
|   `-- sample_autodraft.json
|
|-- src/
|   |-- autodraft_builder.py
|   |-- document_classifier.py
|   |-- document_extractor.py
|   |-- financial_validator.py
|   |-- information_extractor.py
|   |-- master_data.py
|   |-- master_data_resolver.py
|   |-- ocr.py
|   |-- pdf_utils.py
|   |-- pipeline.py
|   |-- run_all.py
|   |-- schema_validator.py
|   |-- validate_all.py
|   `-- validate_erp.py
|
|-- test_documents/
|   |-- run_test_documents.py
|   |-- validate_test_erp.py
|   `-- test PDF documents
|
|-- output/
|   `-- generated JSON outputs
|
|-- app.py
|-- Dockerfile
|-- requirements.txt
|-- DESIGN.md
|-- README.md
`-- .gitignore
```

---

## 4. Requirements

### Python

The project uses Python 3.13.

Install the required Python packages with:

```powershell
pip install -r requirements.txt
```

For local development, a virtual environment can be used:

```powershell
.venv\Scripts\Activate.ps1
```

### OCR

The system uses Tesseract OCR when native PDF text extraction is insufficient.

The OCR implementation supports:

- Tesseract available on the system PATH.
- A custom executable configured through the `TESSERACT_CMD` environment variable.
- The standard Windows Tesseract installation path as a local fallback.
- Docker environments where Tesseract is installed by the provided `Dockerfile`.

---

## 5. Running the System

The main command for processing the assignment documents is:

```powershell
python -m src.run_all
```

The command automatically:

1. Reads PDFs from `candidate_kit/documents/`.
2. Extracts native PDF text when available.
3. Uses OCR when native text is insufficient.
4. Classifies each document.
5. Determines whether it is a payable.
6. Extracts the required accounting information.
7. Resolves available master-data references.
8. Validates financial components.
9. Generates one JSON file per PDF.
10. Writes the results to `output/`.

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

### Payable Document

A payable is represented inside `payables[]`:

```json
{
  "file": "INV-01.pdf",
  "payables": [
    {
      "invoice_type": "INVOICE",
      "currency": "EUR",
      "gross_total": "...",
      "line_items": [],
      "taxes": []
    }
  ],
  "declined": []
}
```

### Credit Memo

A credit memo uses the same AutoDraft schema with:

```json
"invoice_type": "CREDIT_MEMO"
```

Its monetary values use the positive magnitudes stated by the credit memo, consistent with the supplied ERP sign handling.

### Non-Payable Document

A document determined not to be a payable is represented using `declined[]`:

```json
{
  "file": "INV-02.pdf",
  "payables": [],
  "declined": [
    {
      "doc_type": "...",
      "reason": "..."
    }
  ]
}
```

A document can contain zero, one, or multiple payable records.

---

## 7. Document Extraction

The extraction layer first attempts to obtain native text from the PDF.

If the available native text is insufficient, the system:

1. Renders the PDF pages.
2. Runs OCR on the rendered pages.
3. Cleans the extracted text.
4. Passes the resulting text to the downstream pipeline.

This supports both digitally generated PDFs and image-based documents.

---

## 8. Document Classification

Before generating an AutoDraft, the system classifies the document using evidence present in the document.

Signals include:

- Invoice terminology
- Credit memo terminology
- Payment reminder terminology
- Invoice numbers
- Dates
- Payment-related information
- Financial and document signals

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
- Chart of accounts

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

The financial validator acts as a diagnostic consistency layer.

The supplied ERP recomputation is used as the final accounting validation for generated payables.

---

## 12. ERP Validation

The challenge provides `candidate_kit/erp.py` as the ERP recomputation used to determine the gross amount that would be booked from a generated payable.

The project includes:

```text
src/validate_erp.py
```

for validating the generated outputs against the supplied ERP logic.

Run:

```powershell
python -m src.validate_erp
```

Current validation results:

```text
Total payables : 24
ERP PASS       : 24
ERP FAIL       : 0
```

The ERP validation is performed from the generated payable components rather than simply comparing a copied document total.

---

## 13. Structural Validation

The project includes:

```text
src/validate_all.py
```

Run:

```powershell
python -m src.validate_all
```

Current validation results:

```text
Found 42 JSON files.

Valid   : 42
Invalid : 0
```

---

## 14. Validation Results

The implementation was tested on the supplied 42 PDF documents.

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

Additional local test documents were also used to test:

- Standard invoices
- Discount invoices
- Credit memos
- Payment reminders
- Line-level taxes
- Header-level taxes
- Documents with different currencies
- Unseen invoice layouts

---

## 15. Design Principles

The implementation follows these principles.

### 1. Evidence over assumptions

Values are extracted from the document rather than invented.

### 2. Structure over total-only matching

Quantities, prices, discounts, taxes and charges are preserved according to their placement in the document.

### 3. Conservative master-data matching

Internal codes are emitted only when supported by a genuine master-data match.

### 4. Payable vs. non-payable separation

Documents that are not bookable payables are placed in `declined[]`.

### 5. OCR fallback

Image-based documents are processed when native PDF text is insufficient.

### 6. ERP verification

Generated payable components are checked against the supplied ERP recomputation.

---

## 16. Design Documentation

The reasoning behind the extraction strategy, handling of documents unlike those already seen, and exceptional document cases is documented separately in:

```text
DESIGN.md
```

The design document addresses:

- What was learned about the document set.
- How the system handles documents unlike those already seen.
- How the system avoids unsupported guesses.
- Which document required special consideration and why.

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

There is one JSON file corresponding to each input PDF.

Example:

```text
output/
|-- DU-02.json
|-- DU-03.json
|-- DU-05.json
|-- ...
`-- INV-37.json
```

---

## 18. Streamlit Demo

A Streamlit interface is included in:

```text
app.py
```

The interface provides a visual demonstration of the document-intelligence pipeline for an uploaded PDF.

The demo displays the processing stages, including:

- PDF extraction
- OCR fallback
- Document classification
- Information extraction
- Master-data resolution
- Financial validation
- AutoDraft generation
- Output inspection

---

## 19. Docker Deployment

The project includes a `Dockerfile` for containerized execution.

The Docker image installs:

- Python 3.13
- Tesseract OCR
- Project Python dependencies

The container starts the Streamlit application.

Build the image with:

```bash
docker build -t zycus-ai-document-intelligence .
```

Run it with:

```bash
docker run -p 8501:8501 zycus-ai-document-intelligence
```

The Streamlit application can then be accessed locally at:

```text
http://localhost:8501
```

---

## 20. Scope

The implementation focuses on the requirements of the assignment:

- Document understanding
- Payable classification
- Financial information extraction
- Master-data resolution
- Financial structure preservation
- Financial validation
- ERP validation
- JSON AutoDraft generation
- OCR fallback
- Non-payable identification

The system does not introduce external accounting assumptions into generated records.

---

## 21. Final Submission Contents

The submission package contains:

- Working source code
- Assignment schema and ERP logic
- Master-data files
- Generated `output/*.json` files
- `DESIGN.md`
- `README.md`
- `requirements.txt`
- `Dockerfile`
- Streamlit demonstration application
- Local test documents and validation scripts

The Python virtual environment, Git metadata, debug artifacts, temporary OCR files, and generated rendering/debug directories are excluded from the submission package.
