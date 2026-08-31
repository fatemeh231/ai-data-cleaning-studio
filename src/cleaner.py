# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 11:53:47 2026

@author: fatemeh
"""


# src/cleaner.py
# Core data cleaning logic - 10 operations for the AI Data Cleaning Studio

import pandas as pd
import re
import numpy as np
from src.config import FEATURES

# ============================================
# 1. STANDARDIZE DATES
# ============================================
def standardize_dates(df):
    """
    Detect columns with date-like strings and convert them to 
    standard YYYY-MM-DD format.
    """
    date_fixed = 0
    df_copy = df.copy()
    
    for col in df_copy.columns:
        # Only try to convert object/string columns
        if df_copy[col].dtype == 'object':
            # Try to convert to datetime
            try:
                converted = pd.to_datetime(df_copy[col], errors='coerce')
                # If at least 50% of values converted successfully, apply it
                if converted.notna().sum() > len(converted) * 0.5:
                    df_copy[col] = converted
                    date_fixed += 1
            except:
                pass  # Skip columns that don't convert
    
    return df_copy, {"dates_fixed": date_fixed}


# ============================================
# 2. CLEAN TEXT (Trim, Case, Special Chars)
# ============================================
def clean_text(df):
    """
    Trim whitespace, standardize case, remove special characters
    from text columns.
    """
    text_fixed = 0
    df_copy = df.copy()
    
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            # Convert to string and strip leading/trailing spaces
            df_copy[col] = df_copy[col].astype(str).str.strip()
            
            # Replace multiple spaces with single space
            df_copy[col] = df_copy[col].str.replace(r'\s+', ' ', regex=True)
            
            # Remove special characters (keep letters, numbers, and spaces)
            df_copy[col] = df_copy[col].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            
            text_fixed += 1
    
    return df_copy, {"text_fixed": text_fixed}


# ============================================
# 3. CLEAN NUMERIC (Remove commas, fix types)
# ============================================
def clean_numeric(df):
    """
    Remove commas, currency symbols, and convert to proper numeric types.
    """
    numeric_fixed = 0
    df_copy = df.copy()
    
    for col in df_copy.columns:
        # Try to clean if it's object/string
        if df_copy[col].dtype == 'object':
            # Remove $, commas, and convert to float
            cleaned = df_copy[col].astype(str).str.replace(r'[\$,]', '', regex=True)
            cleaned = pd.to_numeric(cleaned, errors='coerce')
            
            # If at least 70% converted, apply it
            if cleaned.notna().sum() > len(cleaned) * 0.7:
                df_copy[col] = cleaned
                numeric_fixed += 1
    
    return df_copy, {"numeric_fixed": numeric_fixed}


# ============================================
# 4. STANDARDIZE CATEGORIES
# ============================================
def clean_categorical(df):
    """
    Standardize categorical values (e.g., "male"/"Male"/"M" → "Male").
    """
    categorical_fixed = 0
    df_copy = df.copy()
    
    # Common mapping for standard categories
    category_map = {
        # Gender
        'm': 'Male', 'male': 'Male', 'M': 'Male',
        'f': 'Female', 'female': 'Female', 'F': 'Female',
        'non-binary': 'Non-Binary', 'nb': 'Non-Binary',
        # Yes/No
        'y': 'Yes', 'yes': 'Yes', 'Y': 'Yes',
        'n': 'No', 'no': 'No', 'N': 'No',
        # True/False
        'true': 'True', 't': 'True', '1': 'True',
        'false': 'False', 'f': 'False', '0': 'False'
    }
    
    for col in df_copy.columns:
        if df_copy[col].dtype == 'object':
            # Convert to string, strip, lowercase for mapping
            series = df_copy[col].astype(str).str.strip().str.lower()
            
            # Apply mapping where possible
            mapped = series.map(category_map)
            
            # If mapping converted at least 30% of values, apply it
            if mapped.notna().sum() > len(mapped) * 0.3:
                df_copy[col] = mapped.fillna(df_copy[col])
                categorical_fixed += 1
            else:
                # If no standard mapping, at least strip and title-case
                df_copy[col] = df_copy[col].astype(str).str.strip().str.title()
    
    return df_copy, {"categorical_fixed": categorical_fixed}


# ============================================
# 5. REMOVE DUPLICATES
# ============================================
def remove_duplicates(df):
    """
    Remove duplicate rows from the dataset.
    """
    original_len = len(df)
    df_copy = df.drop_duplicates(keep='first')
    duplicates_removed = original_len - len(df_copy)
    
    return df_copy, {"duplicates_removed": duplicates_removed}


# ============================================
# 6. FILL MISSING VALUES (Mean/Mode/Median)
# ============================================
def fill_missing_values(df):
    """
    Intelligently fill missing values:
    - Numeric: fill with median
    - Categorical: fill with mode
    - Text: fill with "Unknown"
    """
    missing_filled = 0
    df_copy = df.copy()
    
    for col in df_copy.columns:
        if df_copy[col].isna().sum() > 0:
            if df_copy[col].dtype in ['int64', 'float64']:
                # Numeric → median
                median_val = df_copy[col].median()
                df_copy[col].fillna(median_val, inplace=True)
                missing_filled += 1
            elif df_copy[col].dtype == 'object':
                # Check if it's categorical (few unique values)
                if df_copy[col].nunique() < len(df_copy) * 0.3:
                    # Categorical → mode
                    mode_val = df_copy[col].mode()[0] if not df_copy[col].mode().empty else "Unknown"
                    df_copy[col].fillna(mode_val, inplace=True)
                else:
                    # Text → "Unknown"
                    df_copy[col].fillna("Unknown", inplace=True)
                missing_filled += 1
    
    return df_copy, {"missing_filled": missing_filled}


# ============================================
# 7. REMOVE OUTLIERS (Premium - Marked for future)
# ============================================
def remove_outliers(df):
    """
    Remove outliers using IQR method.
    NOTE: This is a PREMIUM feature. In demo, we just return the df unchanged.
    """
    # In demo, we do nothing. Full version would implement this.
    return df, {"outliers_removed": 0}


# ============================================
# 8. STANDARDIZE PHONE NUMBERS (Premium)
# ============================================
def standardize_phones(df):
    """
    Standardize phone numbers to international format.
    NOTE: This is a PREMIUM feature. In demo, we just return the df unchanged.
    """
    return df, {"phones_fixed": 0}


# ============================================
# 9. MASK PII (Premium - Not in Demo)
# ============================================
def mask_pii(df):
    """
    Mask PII (emails, phones, IDs).
    NOTE: This is a PREMIUM feature. In demo, we just return the df unchanged.
    """
    return df, {"pii_masked": 0}


# ============================================
# 10. BATCH PROCESSING (Premium - Not in Demo)
# ============================================
def batch_process(df):
    """
    Process multiple files at once.
    NOTE: This is a PREMIUM feature. In demo, we just return the df unchanged.
    """
    return df, {"batch_processed": 0}


# ============================================
# MAIN ORCHESTRATOR: clean_data()
# ============================================
def clean_data(df):
    """
    Main function that runs all cleaning operations in sequence.
    Returns: (cleaned_dataframe, results_dictionary)
    """
    results = {}
    df_clean = df.copy()
    
    # ========== CORE CLEANING (Always available in demo) ==========
    
    # 1. Remove Duplicates
    df_clean, dup_result = remove_duplicates(df_clean)
    results.update(dup_result)
    
    # 2. Clean Text
    df_clean, text_result = clean_text(df_clean)
    results.update(text_result)
    
    # 3. Clean Numeric
    df_clean, num_result = clean_numeric(df_clean)
    results.update(num_result)
    
    # 4. Standardize Categories
    df_clean, cat_result = clean_categorical(df_clean)
    results.update(cat_result)
    
    # 5. Standardize Dates
    df_clean, date_result = standardize_dates(df_clean)
    results.update(date_result)
    
    # 6. Fill Missing Values
    df_clean, missing_result = fill_missing_values(df_clean)
    results.update(missing_result)
    
    # ========== PREMIUM FEATURES (Skip in demo) ==========
    # These are here for structure but return nothing in demo
    
    if FEATURES.get("outlier_detection", False):
        df_clean, outlier_result = remove_outliers(df_clean)
        results.update(outlier_result)
    
    if FEATURES.get("pii_masking", False):
        df_clean, mask_result = mask_pii(df_clean)
        results.update(mask_result)
    
    # Add total rows processed
    results["rows_processed"] = len(df_clean)
    
    return df_clean, results