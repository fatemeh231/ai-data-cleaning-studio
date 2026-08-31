# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 11:58:08 2026

@author: fatemeh
"""

# run_demo.py
# RUN THIS FILE (F5) to test your cleaning engine.
# It fixes Python's path so it always finds the 'src' folder.

import os
import sys
import pandas as pd

# ============================================
# FIX: Tell Python where the project root is
# ============================================

# Get the absolute path of THIS file (which is in the project root)
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to Python's search path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Change the working directory to the project root
os.chdir(project_root)

# ============================================
# NOW we can safely import from 'src'
# ============================================

from src import cleaner

# ============================================
# Create a messy sample dataset to test
# ============================================

test_df = pd.DataFrame({
    'Name': ['  john doe  ', 'JANE DOE', 'bob smith', 'alice   '],
    'Date': ['12/31/2024', '2024-01-01', 'Jan 5, 2024', '2023/12/25'],
    'Salary': ['$1,000', '$2,500', '$3,000', '$4,200'],
    'Gender': ['M', 'F', 'm', 'female'],
    'Status': ['active', 'inactive', 'Active', 'INACTIVE']
})

print("=" * 50)
print("🔍 ORIGINAL DATA")
print("=" * 50)
print(test_df)
print("\n")

# ============================================
# RUN THE CLEANER
# ============================================

print("🧹 RUNNING CLEANER...")
cleaned_df, results = cleaner.clean_data(test_df)

print("=" * 50)
print("✨ CLEANED DATA")
print("=" * 50)
print(cleaned_df)
print("\n")

print("=" * 50)
print("📊 CLEANING RESULTS")
print("=" * 50)
for key, value in results.items():
    print(f"  {key}: {value}")