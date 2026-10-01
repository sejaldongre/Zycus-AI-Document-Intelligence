# DESIGN.md

## Bookable Payable — Document Intelligence System

### 1. What did I eventually understand about these documents that I did not understand on day one?

On day one, the problem initially looked like a conventional invoice-extraction task: identify fields such as invoice number, date, supplier, currency, line items, taxes and total, then place them into the provided JSON schema.

By working through the documents and validating the generated records against the supplied ERP recomputation, it became clear that the real problem is different.

A payable is not correct merely because the extracted fields visually resemble the document or because the final total happens to match. The accounting structure matters. The ERP rebuilds the gross amount from the components supplied in the autodraft, so the system must preserve how the document represents quantities, unit prices, discounts, taxes and charges.

This led to three important design decisions:

1. **Document classification comes before payable extraction.**

   The system first determines whether a document is an invoice, credit memo, reminder or another non-payable document. A document that is not a payable is placed in `declined[]` instead of being forced into the payable schema.

2. **Extraction preserves document structure.**

   Line-level taxes remain on the corresponding line. Header-level taxes remain in the header. Quantities, net unit prices, discounts and charges remain decomposed instead of being collapsed into a manually balanced total.

3. **ERP validation is treated as a separate correctness check.**

   The system does not use the document total alone as proof that an autodraft is correct. The supplied components are passed through the same ERP recomputation used by the challenge so that the generated structure is checked independently.

The documents also demonstrated that native PDF text cannot be assumed to be available or reliable. The extraction layer therefore first attempts native text extraction and falls back to OCR when the available text is insufficient.

Finally, master data is a separate concern from document extraction. A supplier name, tax, buyer organisation, payment term or PO printed on a document must be resolved against the supplied master data. If there is no genuine match, the system leaves the corresponding internal code blank instead of inventing one.

---

### 2. When the system meets a document unlike any it has seen, what does it actually do, and why does that generalise instead of guessing?

For an unseen document, the system follows the same pipeline rather than selecting a document-specific answer.

The processing flow is:

```text
PDF
 ↓
Native text extraction
 ↓
OCR fallback when required
 ↓
Document classification
 ↓
Information extraction
 ↓
Master-data resolution
 ↓
Financial/component validation
 ↓
Autodraft generation
 ↓
ERP recomputation
 ↓
output/X.json
```

The extraction layer uses evidence present in the document, such as invoice terminology, dates, amounts, supplier information, tax information, payment information and line-item patterns.

The classifier uses document evidence to distinguish payable documents from documents such as payment reminders and other non-payables. This prevents an unfamiliar non-payable document from being converted into a payable simply because it contains an amount.

For payable documents, the extractor attempts to preserve the values and relationships actually present on the page. It does not invent missing values merely to make the accounting equation balance.

Master-data resolution is deliberately conservative. Exact and normalized matches are attempted against the supplied reference data. An internal code is emitted only when a genuine master-data match exists. If no match exists, leaving the code blank is treated as a valid result.

The financial validation layer checks the consistency of extracted components. The ERP validation then checks whether those components produce the document's bookable gross.

This approach generalises because a new document is processed through the same evidence → extraction → resolution → validation pipeline. It does not require knowing the expected answer for a particular filename or document.

The most important protection against incorrect automation is therefore **not guessing**. When evidence is insufficient, the system keeps the corresponding field blank or declines the document instead of manufacturing a value.

---

### 3. Was there a document that could not be solved the way the others were? If so, which, and how did I know?

The main exception encountered during development was **DU-02**, a customs consolidated invoice.

Most documents could be interpreted through their invoice structure and extracted text. DU-02 contained multiple detailed customs-invoice sections and a consolidated payable amount. OCR successfully captured much of the document but did not reliably capture the consolidated total from the relevant page.

This demonstrated an important limitation of treating OCR text as the complete source of truth: a value can exist visually on a page while being absent or corrupted in OCR output.

DU-02 therefore required page-level visual verification to establish the consolidated payable amount. The extracted result was then validated against the ERP recomputation.

This case reinforced the need for the extraction layer to support multiple representations of a document rather than assuming that missing OCR text means the value does not exist.

There is also a broader class of information that cannot necessarily be obtained from the supplier document itself: internal ERP identifiers such as supplier IDs, payment-term IDs or tax codes may not be printed on the document. Those values are resolved from the supplied master data. When the document value has no genuine master-data match, the system intentionally leaves the internal code blank.

This distinction is important because the system separates **facts stated by the supplier document** from **internal identifiers supplied by the ERP reference data**, rather than inventing internal identifiers.

---

## Validation Summary

The final implementation was tested against the supplied documents.

- 42 PDF documents processed successfully.
- 42/42 generated JSON files passed structural validation.
- 24 payable records were generated.
- All 24 payable records passed the supplied ERP recomputation.
- ERP pass rate: 100%.
- No payable failed ERP recomputation.
- Non-payable documents were emitted in `declined[]`.
- Output files were generated as `output/X.json` for the processed documents.

The implementation therefore treats the task as an accounting-document reasoning problem rather than simple field extraction: identify the document, preserve its financial structure, resolve only supported master data, avoid invented values, and validate the resulting components through the ERP calculation.
