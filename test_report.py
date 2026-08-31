# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:10:43 2026

@author: fatemeh
"""

# test_report.py
# Test PDF Report Generator

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

from src import cleaner, report_generator
import pandas as pd

# Create sample messy data
test_df = pd.DataFrame({
    'Name': ['  john doe  ', 'JANE DOE', 'bob smith', 'alice   '],
    'Date': ['12/31/2024', '2024-01-01', 'Jan 5, 2024', '2023/12/25'],
    'Salary': ['$1,000', '$2,500', '$3,000', '$4,200'],
    'Gender': ['M', 'F', 'm', 'female'],
    'Email': ['john@example.com', 'jane@gmail.com', 'bob@company.com', 'alice@work.com'],
})

print("🧹 Cleaning data...")
cleaned_df, results = cleaner.clean_data(test_df)

print("📄 Generating PDF report...")
pdf_path = report_generator.generate_pdf_report(
    original_df=test_df,
    cleaned_df=cleaned_df,
    cleaning_results=results,
)

print(f"✅ Report generated: {pdf_path}")
print(f"📁 File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
print(f"🔍 Open it in your PDF viewer to see the result!")