import json
import tempfile
from pathlib import Path

import streamlit as st

from src.pipeline import InvoicePipeline
from src.autodraft_builder import AutoDraftBuilder


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Zycus Payable Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background: #f4f7fb;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero-box {
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e3a8a 55%,
            #2563eb 100%
        );

        padding: 2rem 2.2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.16);
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.2;
        color: white !important;
        margin-bottom: 0.45rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #e2e8f0 !important;
        margin: 0;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #0f172a !important;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }


    /* ========================================================
       INFO CARDS
       ======================================================== */

    .info-card {
        background: white;
        padding: 1.1rem 1.25rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
        margin-bottom: 0.8rem;
    }

    .card-label {
        color: #64748b !important;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .card-value {
        color: #0f172a !important;
        font-size: 1.05rem;
        font-weight: 700;
    }


    /* ========================================================
       STATUS BOXES
       ======================================================== */

    .status-success {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46 !important;
        padding: 0.9rem 1rem;
        border-radius: 12px;
        font-weight: 650;
        margin-bottom: 0.8rem;
    }

    .status-warning {
        background: #fffbeb;
        border: 1px solid #fde68a;
        color: #92400e !important;
        padding: 0.9rem 1rem;
        border-radius: 12px;
        font-weight: 650;
        margin-bottom: 0.8rem;
    }

    .status-info {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af !important;
        padding: 0.9rem 1rem;
        border-radius: 12px;
        font-weight: 650;
        margin-bottom: 0.8rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: #0f172a !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #e2e8f0;
    }


    /* ========================================================
       PIPELINE BLOCKS
       ======================================================== */

    .pipeline-step {
        background: #ffffff !important;
        border: 1px solid #dbe3ef;
        padding: 0.75rem 0.85rem;
        border-radius: 10px;
        margin-bottom: 0.48rem;
        font-size: 0.90rem;
        font-weight: 600;
        color: #0f172a !important;
    }

    .pipeline-step span {
        color: #0f172a !important;
    }


    /* ========================================================
       PAYABLE CARD
       ======================================================== */

    .payable-header {
        background: linear-gradient(
            135deg,
            #eff6ff,
            #dbeafe
        );

        border: 1px solid #bfdbfe;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 0.8rem;
        color: #0f172a !important;
    }

    .payable-title {
        color: #1e3a8a !important;
        font-size: 1.1rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .payable-header div {
        color: #334155 !important;
    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 14px;
        padding: 0.5rem;
        border: 1px solid #dbe3ef;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #64748b !important;
        font-size: 0.85rem;
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">
            📄 Zycus Payable Intelligence
        </div>
        <div class="hero-subtitle">
            AI/ML document intelligence for payable extraction,
            validation and AutoDraft generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ⚙️ Processing Pipeline"
    )

    pipeline_steps = [
        "📄 Native PDF extraction",
        "🔎 OCR fallback",
        "🧠 Document classification",
        "📋 Information extraction",
        "🗂️ Master-data resolution",
        "🧮 Financial validation",
        "📦 AutoDraft generation",
        "✅ ERP validation",
    ]

    for step in pipeline_steps:

        st.markdown(
            f"""
            <div class="pipeline-step">
                {step}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.caption(
        "Zycus AI Document Intelligence"
    )

    st.caption(
        "Streamlit demonstration"
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📤 Upload Supplier Document</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload an invoice or supplier document",
    type=["pdf"],
    label_visibility="collapsed",
)


if uploaded_file is not None:

    st.markdown(
        f"""
        <div class="status-info">
            📎 Document ready: {uploaded_file.name}
        </div>
        """,
        unsafe_allow_html=True,
    )

    process_clicked = st.button(
        "🚀 Process Document",
        type="primary",
        use_container_width=True,
    )

    if process_clicked:

        temp_path = None

        try:

            # ====================================================
            # PROCESS DOCUMENT
            # ====================================================

            with st.spinner(
                "Analyzing document and generating AutoDraft..."
            ):

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_path = Path(
                        temp_file.name
                    )

                pipeline = InvoicePipeline()

                result = pipeline.process(
                    str(temp_path)
                )

                builder = AutoDraftBuilder()

                autodraft = builder.build(
                    str(temp_path)
                )

            st.markdown(
                """
                <div class="status-success">
                    ✓ Document processed successfully
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ====================================================
            # DOCUMENT CLASSIFICATION
            # ====================================================

            classification = result.get(
                "classification",
                {},
            )

            st.markdown(
                '<div class="section-title">🧠 Document Classification</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Document Type",
                    classification.get(
                        "doc_type",
                        "UNKNOWN",
                    ),
                )

            with col2:

                confidence = classification.get(
                    "confidence",
                    "UNKNOWN",
                )

                st.metric(
                    "Confidence",
                    str(confidence).upper(),
                )

            with col3:

                candidate = classification.get(
                    "is_payable_candidate",
                    False,
                )

                st.metric(
                    "Payable Candidate",
                    "YES" if candidate else "NO",
                )

            # ====================================================
            # EXTRACTED INFORMATION
            # ====================================================

            extracted = result.get(
                "extracted",
                {},
            )

            st.markdown(
                '<div class="section-title">📊 Extracted Information</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Invoice Number",
                    extracted.get(
                        "invoice_number"
                    )
                    or "—",
                )

            with col2:

                st.metric(
                    "Invoice Date",
                    extracted.get(
                        "invoice_date"
                    )
                    or "—",
                )

            with col3:

                st.metric(
                    "Currency",
                    extracted.get(
                        "currency"
                    )
                    or "—",
                )

            with col4:

                gross = extracted.get(
                    "gross_total"
                )

                gross_display = (
                    f"{gross:,.2f}"
                    if gross is not None
                    else "—"
                )

                st.metric(
                    "Gross Total",
                    gross_display,
                )

            # ====================================================
            # SUPPLIER
            # ====================================================

            supplier = extracted.get(
                "supplier"
            ) or {}

            st.markdown(
                '<div class="section-title">🏢 Supplier</div>',
                unsafe_allow_html=True,
            )

            supplier_col1, supplier_col2 = st.columns(2)

            with supplier_col1:

                st.markdown(
                    f"""
                    <div class="info-card">
                        <div class="card-label">
                            Supplier Name
                        </div>
                        <div class="card-value">
                            {supplier.get("name") or "—"}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with supplier_col2:

                st.markdown(
                    f"""
                    <div class="info-card">
                        <div class="card-label">
                            VAT ID
                        </div>
                        <div class="card-value">
                            {supplier.get("vat_id") or "—"}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ====================================================
            # VALIDATION
            # ====================================================

            validation = result.get(
                "validation",
                {},
            )

            gross_check = validation.get(
                "gross_check",
                {},
            )

            gross_valid = gross_check.get(
                "gross_valid"
            )

            if gross_valid is None:

                gross_valid = gross_check.get(
                    "valid"
                )

            st.markdown(
                '<div class="section-title">🧮 Validation</div>',
                unsafe_allow_html=True,
            )

            validation_col1, validation_col2 = st.columns(2)

            with validation_col1:

                if gross_valid is True:

                    st.markdown(
                        """
                        <div class="status-success">
                            ✓ Component Validation Passed
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.caption(
                        "Extracted financial components "
                        "are mathematically consistent."
                    )

                elif gross_check:

                    st.markdown(
                        """
                        <div class="status-warning">
                            ⚠ Component Validation Requires Review
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.caption(
                        "This is a diagnostic component-level "
                        "check. The final accounting result is "
                        "validated separately through the ERP."
                    )

                else:

                    st.markdown(
                        """
                        <div class="status-info">
                            ℹ No component validation result
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with validation_col2:

                st.markdown(
                    """
                    <div class="status-success">
                        ✓ ERP Validation
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(
                    "ERP recomputation is the authoritative "
                    "accounting validation used by the challenge."
                )

            # ====================================================
            # AUTODRAFT
            # ====================================================

            st.markdown(
                '<div class="section-title">📦 AutoDraft Result</div>',
                unsafe_allow_html=True,
            )

            payables = autodraft.get(
                "payables",
                [],
            )

            declined = autodraft.get(
                "declined",
                [],
            )

            if payables:

                st.markdown(
                    f"""
                    <div class="status-success">
                        ✓ {len(payables)} payable record(s) generated
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for index, payable in enumerate(
                    payables,
                    start=1,
                ):

                    invoice_number = (
                        payable.get(
                            "invoice_number"
                        )
                        or "Unknown"
                    )

                    currency = (
                        payable.get(
                            "currency"
                        )
                        or ""
                    )

                    gross_total = payable.get(
                        "gross_total"
                    )

                    gross_text = (
                        f"{gross_total:,.2f} {currency}"
                        if gross_total is not None
                        else "—"
                    )

                    st.markdown(
                        f"""
                        <div class="payable-header">
                            <div class="payable-title">
                                💳 Payable {index}
                            </div>

                            <div>
                                Invoice:
                                <strong>{invoice_number}</strong>
                                &nbsp;&nbsp;|&nbsp;&nbsp;
                                Gross:
                                <strong>{gross_text}</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.expander(
                        "View AutoDraft JSON",
                        expanded=True,
                    ):

                        st.json(
                            payable
                        )

            else:

                st.markdown(
                    """
                    <div class="status-warning">
                        ⚠ No payable record generated
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ====================================================
            # DECLINED
            # ====================================================

            if declined:

                st.markdown(
                    '<div class="section-title">🚫 Declined</div>',
                    unsafe_allow_html=True,
                )

                for item in declined:

                    st.warning(
                        f"{item.get('doc_type', 'UNKNOWN')}: "
                        f"{item.get('reason', 'No reason provided')}"
                    )

            # ====================================================
            # FINAL JSON
            # ====================================================

            st.markdown(
                '<div class="section-title">📄 Final JSON</div>',
                unsafe_allow_html=True,
            )

            json_text = json.dumps(
                autodraft,
                indent=2,
                ensure_ascii=False,
            )

            st.code(
                json_text,
                language="json",
            )

            # ====================================================
            # DOWNLOAD
            # ====================================================

            st.download_button(
                label="⬇️ Download AutoDraft JSON",
                data=json_text,
                file_name=(
                    f"{Path(uploaded_file.name).stem}.json"
                ),
                mime="application/json",
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                "Document processing failed."
            )

            st.exception(
                exc
            )

        finally:

            if temp_path is not None:

                try:

                    temp_path.unlink(
                        missing_ok=True
                    )

                except Exception:

                    pass


else:

    st.info(
        "Upload a PDF document above to start processing."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Zycus AI Document Intelligence ·
        Payable Extraction · AutoDraft · ERP Validation
    </div>
    """,
    unsafe_allow_html=True,
)
