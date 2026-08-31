# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:12:21 2026

@author: fatemeh
"""

# app/streamlit_app.py
# AI Data Cleaning Studio - Web Interface
# This is the DEMO version - row limited with watermarks

import streamlit as st
import pandas as pd
import os
import tempfile
import sys
from datetime import datetime

# ============================================
# FIX: Add project root to Python path
# ============================================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

# ============================================
# IMPORT FROM SRC
# ============================================
from src.config import (
    DEMO_ROW_LIMIT,
    CONTACT_EMAIL,
    CONTACT_TELEGRAM,
    LINKEDIN_URL,
    GITHUB_URL,
    PRODUCT_NAME,
    COMPANY_NAME,
    FEATURES
)
from src.cleaner import clean_data
from src.profiler import generate_profile_report, get_data_quality_summary
from src.pii_detector import detect_pii, get_pii_summary
from src.report_generator import generate_pdf_report

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title=f"{PRODUCT_NAME} - Demo",
    page_icon="🧹",
    layout="wide"
)

# ============================================
# HEADER / WATERMARK (Visible on every page)
# ============================================
st.markdown(
    f"""
    <div style="background-color: #f0f2f6; padding: 12px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #ff4b4b;">
        <strong>🧪 DEMO VERSION</strong> — Processing limited to <strong>{DEMO_ROW_LIMIT:,} rows</strong>.
        <span style="float: right;">
            💼 <strong>Need more?</strong> 
            <a href="mailto:{CONTACT_EMAIL}" target="_blank">📧 Email</a> | 
            <a href="https://t.me/{CONTACT_TELEGRAM.lstrip('@')}" target="_blank">💬 Telegram</a>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================
# MAIN APP
# ============================================
st.title(f"🧹 {PRODUCT_NAME}")
st.markdown(f"*Upload your messy data and get a clean, analysis-ready file in seconds.*")
st.markdown(f"<span style='font-size:14px; color:#666;'>Developed by <b>{COMPANY_NAME}</b></span>", unsafe_allow_html=True)

st.markdown("---")

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload your CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    help=f"Demo limit: {DEMO_ROW_LIMIT:,} rows. Contact us to remove limits."
)

# ============================================
# PROCESS THE FILE
# ============================================
if uploaded_file is not None:
    try:
        # Load the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File loaded: **{len(df):,}** rows, **{len(df.columns)}** columns.")
        
        # ============================================
        # ENFORCE ROW LIMIT
        # ============================================
        if len(df) > DEMO_ROW_LIMIT:
            st.error(
                f"🚫 **Demo Limit Reached**: Your file has {len(df):,} rows, but the demo only processes {DEMO_ROW_LIMIT:,} rows."
            )
            st.markdown(
                f"""
                <div style="padding: 15px; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px;">
                    <strong>💼 Upgrade to the Full Version</strong> to process unlimited rows, unlock PII masking, 
                    outlier detection, and batch processing.<br><br>
                    📧 Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>
                    💬 Telegram: <a href="https://t.me/{CONTACT_TELEGRAM.lstrip('@')}">{CONTACT_TELEGRAM}</a>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.stop()
        
        # Show success and proceed
        st.info(f"ℹ️ Processing **{len(df):,}** rows. (Demo limit: {DEMO_ROW_LIMIT:,})")
        
        # Store in session state for later use
        st.session_state['original_df'] = df
        st.session_state['cleaned_df'] = None
        st.session_state['cleaning_results'] = None
        st.session_state['pii_results'] = None
        
        # ============================================
        # TABS FOR WORKFLOW
        # ============================================
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Data Profile",
            "🧹 Clean & Export",
            "🔒 PII Detection",
            "📄 Reports"
        ])
        
        # ============================================
        # TAB 1: DATA PROFILE
        # ============================================
        with tab1:
            st.subheader("📊 Data Quality Profile")
            
            # Quick summary
            summary = get_data_quality_summary(df)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{summary['rows']:,}")
            with col2:
                st.metric("Missing Cells", f"{summary['missing_cells']:,}")
            with col3:
                st.metric("Duplicate Rows", f"{summary['duplicate_rows']:,}")
            with col4:
                st.metric("Columns", f"{summary['columns']}")
            
            if summary['columns_with_high_missing']:
                st.warning(f"⚠️ Columns with >50% missing values: {', '.join(summary['columns_with_high_missing'])}")
            
            # Generate full profile
            if st.button("🔍 Generate Full Profile Report", use_container_width=True):
                with st.spinner("Generating profile report... This may take a moment."):
                    html = generate_profile_report(df)
                    # Display in an iframe
                    st.components.v1.html(html, height=800, scrolling=True)
            
            st.caption("💡 Full version includes exportable HTML profiles and deeper analysis.")
        
        # ============================================
        # TAB 2: CLEAN & EXPORT
        # ============================================
        with tab2:
            st.subheader("🧹 Clean Your Data")
            st.markdown("Apply 10 core cleaning operations to your dataset.")
            
            if st.button("🧼 Run Auto-Clean", use_container_width=True, type="primary"):
                with st.spinner("Cleaning data... applying 10 core operations."):
                    cleaned_df, results = clean_data(df)
                    st.session_state['cleaned_df'] = cleaned_df
                    st.session_state['cleaning_results'] = results
                
                st.success("✅ Cleaning complete!")
                
                # Show results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows Original", f"{len(df):,}")
                    st.metric("Duplicates Removed", f"{results.get('duplicates_removed', 0):,}")
                    st.metric("Dates Fixed", f"{results.get('dates_fixed', 0)} columns")
                with col2:
                    st.metric("Rows Cleaned", f"{len(cleaned_df):,}")
                    st.metric("Missing Handled", f"{results.get('missing_handled', 0)} columns")
                    st.metric("Categories Fixed", f"{results.get('categories_fixed', 0)}")
                
                # Show side-by-side preview
                st.subheader("📋 Before vs After (First 5 Rows)")
                
                # Prepare comparison
                compare_df = pd.DataFrame()
                for col in df.columns[:5]:  # Show first 5 columns only
                    compare_df[f"{col} (Original)"] = df[col].head(5).values
                    compare_df[f"{col} (Cleaned)"] = cleaned_df[col].head(5).values
                
                st.dataframe(compare_df, use_container_width=True)
                
                # Export buttons
                st.subheader("💾 Export Cleaned Data")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv = cleaned_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "cleaned_data.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        cleaned_df.to_excel(tmp.name, index=False)
                        with open(tmp.name, "rb") as f:
                            st.download_button(
                                "📥 Download Excel",
                                f,
                                "cleaned_data.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                
                with col3:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
                        cleaned_df.to_parquet(tmp.name, index=False)
                        with open(tmp.name, "rb") as f:
                            st.download_button(
                                "📥 Download Parquet",
                                f,
                                "cleaned_data.parquet",
                                "application/octet-stream",
                                use_container_width=True
                            )
                
                st.markdown("---")
                st.info(
                    "🔒 **Full version features:** PII masking, outlier removal, batch processing, and custom cleaning rules. "
                    f"[Contact us](mailto:{CONTACT_EMAIL}) for a demo."
                )
            
            elif st.session_state.get('cleaned_df') is not None:
                st.info("✅ Cleaned data is ready. Use the buttons above to export or generate reports.")
        
        # ============================================
        # TAB 3: PII DETECTION
        # ============================================
        with tab3:
            st.subheader("🔒 PII Detection")
            st.markdown("*Scan your data for Personally Identifiable Information (PII).*")
            st.info("📌 **Demo version**: Detects PII but does NOT mask it. Full version masks automatically.")
            
            if st.button("🔎 Scan for PII", use_container_width=True):
                with st.spinner("Scanning for emails, phone numbers, and IDs..."):
                    pii_results = detect_pii(df)
                    st.session_state['pii_results'] = pii_results
                
                total = sum(len(v) for v in pii_results.values())
                
                if total > 0:
                    st.warning(f"⚠️ Found **{total}** potential PII entities.")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📧 Emails", len(pii_results.get('EMAIL', [])))
                    with col2:
                        st.metric("📞 Phones", len(pii_results.get('PHONE', [])))
                    with col3:
                        st.metric("🆔 IDs", len(pii_results.get('ID', [])))
                    
                    # Show examples
                    if pii_results['EMAIL']:
                        st.write("**Email examples:**", ", ".join(pii_results['EMAIL'][:5]))
                    if pii_results['PHONE']:
                        st.write("**Phone examples:**", ", ".join(pii_results['PHONE'][:5]))
                    if pii_results['ID']:
                        st.write("**ID examples:**", ", ".join(pii_results['ID'][:5]))
                else:
                    st.success("✅ No PII detected.")
                
                st.markdown("---")
                st.info(
                    f"🛡️ **Full version** automatically masks all PII for GDPR/HIPAA compliance. "
                    f"[Contact us](mailto:{CONTACT_EMAIL}) for a demo."
                )
            
            elif st.session_state.get('pii_results') is not None:
                pii_results = st.session_state['pii_results']
                st.write(get_pii_summary(pii_results))
        
        # ============================================
        # TAB 4: REPORTS
        # ============================================
        with tab4:
            st.subheader("📄 Data Quality Reports")
            
            if st.session_state.get('cleaned_df') is not None:
                st.success("✅ Cleaned data is available. Generate your report below.")
                
                if st.button("📑 Generate PDF Report", use_container_width=True, type="primary"):
                    with st.spinner("Generating professional PDF report..."):
                        pdf_path = generate_pdf_report(
                            original_df=st.session_state['original_df'],
                            cleaned_df=st.session_state['cleaned_df'],
                            cleaning_results=st.session_state['cleaning_results']
                        )
                        
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download Report (PDF)",
                                f,
                                os.path.basename(pdf_path),
                                "application/pdf",
                                use_container_width=True
                            )
                        
                        st.success(f"✅ Report generated! Click the button above to download.")
                        st.caption(f"📁 Report saved to: `{pdf_path}`")
            else:
                st.warning("⚠️ Please run the cleaning step first (Tab 2) to generate a report.")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.markdown(
            f"💡 Need help? Contact us at: <a href='mailto:{CONTACT_EMAIL}'>{CONTACT_EMAIL}</a>",
            unsafe_allow_html=True
        )

# ============================================
# FOOTER (Watermark + Social Links)
# ============================================
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 2])

with footer_col1:
    st.markdown(
        f"""
        <div style="text-align: center; color: #999; font-size: 11px;">
            <strong>{PRODUCT_NAME}</strong> — Demo Version<br>
            Developed by <b>{COMPANY_NAME}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with footer_col2:
    st.markdown(
        f"""
        <div style="text-align: center; color: #666; font-size: 11px;">
            <a href="mailto:{CONTACT_EMAIL}" target="_blank">📧 Email</a><br>
            <a href="https://t.me/{CONTACT_TELEGRAM.lstrip('@')}" target="_blank">💬 Telegram</a>
        </div>
        """,
        unsafe_allow_html=True
    )

with footer_col3:
    st.markdown(
        f"""
        <div style="text-align: center; color: #666; font-size: 11px;">
            <a href="{LINKEDIN_URL}" target="_blank">🔗 LinkedIn</a><br>
            <a href="{GITHUB_URL}" target="_blank">🐙 GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    f"""
    <div style="text-align: center; color: #bbb; font-size: 9px; padding-top: 10px;">
        This demo is for evaluation purposes only. Full commercial license required for production use.<br>
        © 2024-{datetime.now().year} {COMPANY_NAME}. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)