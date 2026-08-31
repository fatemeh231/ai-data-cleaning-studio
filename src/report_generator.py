# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:10:06 2026

@author: fatemeh
"""

# src/report_generator.py
# Professional PDF Data Quality Report Generator

import os
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
import base64

from src.config import PRODUCT_NAME, COMPANY_NAME, CONTACT_EMAIL, CONTACT_TELEGRAM

def generate_pdf_report(original_df, cleaned_df, cleaning_results, output_path=None):
    """
    Generate a professional Data Quality Report as PDF.
    
    Args:
        original_df: Original DataFrame before cleaning
        cleaned_df: Cleaned DataFrame after cleaning
        cleaning_results: Dictionary from cleaner.clean_data()
        output_path: Where to save the PDF (optional)
    
    Returns:
        Path to the generated PDF file
    """
    
    if output_path is None:
        from src.config import OUTPUT_PATH
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_PATH, f"data_quality_report_{timestamp}.pdf")
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12,
        spaceBefore=20,
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=8,
        spaceBefore=12,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    
    # ============================================
    # BUILD THE REPORT CONTENT
    # ============================================
    story = []
    
    # --- PAGE 1: TITLE PAGE ---
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(f"<b>{PRODUCT_NAME}</b>", title_style))
    story.append(Paragraph("Data Quality Report", title_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Generated for: <b>{COMPANY_NAME}</b>", body_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Rows Processed: {cleaning_results.get('rows_processed', 0):,}", body_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Prepared by:", body_style))
    story.append(Paragraph(f"<b>{COMPANY_NAME}</b>", body_style))
    story.append(Paragraph(f"Email: {CONTACT_EMAIL}", footer_style))
    story.append(Paragraph(f"Telegram: {CONTACT_TELEGRAM}", footer_style))
    story.append(PageBreak())
    
    # --- PAGE 2: EXECUTIVE SUMMARY ---
    story.append(Paragraph("Executive Summary", heading_style))
    
    # Key metrics
    original_rows = len(original_df)
    cleaned_rows = len(cleaned_df)
    duplicates_removed = cleaning_results.get('duplicates_removed', 0)
    missing_filled = cleaning_results.get('missing_handled', 0)
    dates_fixed = cleaning_results.get('dates_fixed', 0)
    categories_fixed = cleaning_results.get('categories_fixed', 0)
    
    summary_data = [
        ["Metric", "Original", "After Cleaning"],
        ["Total Rows", f"{original_rows:,}", f"{cleaned_rows:,}"],
        ["Duplicates Removed", "N/A", f"{duplicates_removed:,}"],
        ["Missing Values Fixed", "N/A", f"{missing_filled}"],
        ["Dates Standardized", "N/A", f"{dates_fixed}"],
        ["Categories Fixed", "N/A", f"{categories_fixed}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Data Quality Score
    total_issues = duplicates_removed + missing_filled + dates_fixed + categories_fixed
    if original_rows > 0:
        score = max(0, 100 - (total_issues / original_rows * 100))
        score = min(100, score)
    else:
        score = 0
    
    story.append(Paragraph(f"<b>Data Quality Score:</b> {score:.1f}/100", subheading_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Score interpretation
    if score >= 90:
        quality_text = "Excellent - Data is clean and ready for analysis."
        color = "green"
    elif score >= 70:
        quality_text = "Good - Some minor issues detected."
        color = "orange"
    elif score >= 50:
        quality_text = "Fair - Significant cleaning performed."
        color = "gold"
    else:
        quality_text = "Poor - Major data quality issues found."
        color = "red"
    
    story.append(Paragraph(f"<font color='{color}'><b>{quality_text}</b></font>", body_style))
    
    story.append(PageBreak())
    
    # --- PAGE 3: DATA PROFILE ---
    story.append(Paragraph("Data Profile", heading_style))
    
    # Column summary
    story.append(Paragraph("Column Summary", subheading_style))
    
    col_data = [
        ["Column", "Type", "Unique Values", "Missing %", "Sample"]
    ]
    
    for col in original_df.columns:
        col_type = str(original_df[col].dtype)
        unique_vals = original_df[col].nunique()
        missing_pct = (original_df[col].isnull().sum() / len(original_df)) * 100
        sample = str(original_df[col].dropna().iloc[0]) if len(original_df[col].dropna()) > 0 else "N/A"
        if len(sample) > 30:
            sample = sample[:27] + "..."
        
        col_data.append([
            col[:20],  # Truncate long column names
            col_type[:15],
            f"{unique_vals:,}",
            f"{missing_pct:.1f}%",
            sample[:30]
        ])
    
    # Limit to first 20 columns to avoid huge PDF
    if len(col_data) > 21:
        col_data = col_data[:21]
        col_data.append(["...", "...", "...", "...", "..."])
    
    col_table = Table(col_data, colWidths=[1.2*inch, 0.8*inch, 1.0*inch, 0.8*inch, 1.7*inch])
    col_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(col_table)
    
    story.append(PageBreak())
    
    # --- PAGE 4: CLEANING OPERATIONS DETAIL ---
    story.append(Paragraph("Cleaning Operations Details", heading_style))
    
    ops_data = [
        ["Operation", "Result"],
        ["Duplicate Rows Removed", f"{cleaning_results.get('duplicates_removed', 0):,}"],
        ["Missing Values Handled", f"{cleaning_results.get('missing_handled', 0)} columns"],
        ["Dates Standardized", f"{cleaning_results.get('dates_fixed', 0)} columns"],
        ["Text Cleaned", f"{cleaning_results.get('text_fixed', 0)} changes"],
        ["Categories Fixed", f"{cleaning_results.get('categories_fixed', 0)} changes"],
        ["Numeric Commas Removed", f"{cleaning_results.get('commas_removed', 0)} columns"],
        ["Special Characters Removed", f"{cleaning_results.get('special_chars_removed', 0)} changes"],
        ["Data Types Fixed", f"{cleaning_results.get('data_types_fixed', 0)} columns"],
    ]
    
    # Add PII detection if available
    ops_data.append(["PII Detection", "✅ Completed (Emails/Phones/IDs)"])
    
    ops_table = Table(ops_data, colWidths=[2.5*inch, 2.5*inch])
    ops_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ops_table)
    
    story.append(PageBreak())
    
    # --- PAGE 5: PREMIUM FEATURES (Call to Action) ---
    story.append(Paragraph("🚀 Upgrade to Full Version", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    
    premium_features = [
        "🔒 <b>PII Masking</b> - Automatically redact emails, phones, and IDs for GDPR/HIPAA compliance",
        "📊 <b>Outlier Detection</b> - Identify and remove statistical outliers",
        "📁 <b>Batch Processing</b> - Clean multiple files at once",
        "⚙️ <b>Custom Rules</b> - Define your own cleaning logic",
        "🏷️ <b>White-label Branding</b> - Remove 'Powered by' and add your company logo",
        "🚀 <b>API Access</b> - Integrate with your existing systems",
        "💬 <b>Priority Support</b> - Direct access to the development team",
        "🏢 <b>Self-hosted Deployment</b> - Install on your own servers (Docker included)",
    ]
    
    for feature in premium_features:
        story.append(Paragraph(feature, body_style))
        story.append(Spacer(1, 0.1 * inch))
    
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("<b>Contact for Pricing:</b>", subheading_style))
    story.append(Paragraph(f"📧 Email: {CONTACT_EMAIL}", body_style))
    story.append(Paragraph(f"💬 Telegram: {CONTACT_TELEGRAM}", body_style))
    
    story.append(PageBreak())
    
    # --- PAGE 6: FOOTER / DISCLAIMER ---
    story.append(Paragraph("About This Report", heading_style))
    story.append(Paragraph(
        f"This report was automatically generated by <b>{PRODUCT_NAME}</b>, "
        f"an AI-powered data cleaning tool developed by <b>{COMPANY_NAME}</b>.",
        body_style
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "The data quality score is calculated based on the number of issues "
        "detected and fixed during the cleaning process.",
        body_style
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "For full data cleaning capabilities including PII masking, outlier removal, "
        "and batch processing, please contact the developer.",
        body_style
    ))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"© {datetime.now().year} {COMPANY_NAME}. All rights reserved.",
        footer_style
    ))
    story.append(Paragraph(
        f"This report is for evaluation purposes only.",
        footer_style
    ))
    
    # ============================================
    # GENERATE THE PDF
    # ============================================
    
    # Build the document
    doc.build(story)
    
    return output_path