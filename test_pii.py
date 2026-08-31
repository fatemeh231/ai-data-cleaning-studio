# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:07:26 2026

@author: fatemeh
"""

# test_pii.py
# Test PII detection

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

from src import pii_detector
import pandas as pd

# Create a dataset with PII
test_df = pd.DataFrame({
    'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
    'Email': ['alice@example.com', 'bob@gmail.com', 'charlie@company.com'],
    'Phone': ['123-456-7890', '(555) 123-4567', '+1 800 555 0199'],
    'SSN': ['123-45-6789', '987-65-4321', None],
    'Note': ['Contact alice@work.com', 'Call 555-111-2222', 'ID: 111-22-3333']
})

print("🔍 Scanning for PII...")
results = pii_detector.detect_pii(test_df)

print("\n📊 PII Detection Results:")
print(f"  Emails found: {len(results['EMAIL'])}")
print(f"  Phones found: {len(results['PHONE'])}")
print(f"  IDs found: {len(results['ID'])}")

print("\n📋 Details:")
if results['EMAIL']:
    print(f"  Emails: {', '.join(results['EMAIL'][:3])}")
if results['PHONE']:
    print(f"  Phones: {', '.join(results['PHONE'][:3])}")
if results['ID']:
    print(f"  IDs: {', '.join(results['ID'][:3])}")

print("\n" + pii_detector.get_pii_summary(results))