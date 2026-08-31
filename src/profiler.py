# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:00:31 2026

@author: fatemeh
"""

# src/profiler.py
# Auto-generates an interactive Data Quality Report using YData Profiling

import pandas as pd
import warnings
from src.config import PRODUCT_NAME, COMPANY_NAME

# Suppress annoying warnings from pandas/profiling
warnings.filterwarnings('ignore')

def generate_profile_report(df):
    """
    Generates an interactive HTML profile report for the given DataFrame.
    Returns the HTML as a string to embed in Streamlit.
    """
    if df.empty:
        return "<h3>⚠️ No data to profile.</h3>"
    
    try:
        from ydata_profiling import ProfileReport
        
        # Create the profile with a custom title
        profile = ProfileReport(
            df,
            title=f"{PRODUCT_NAME} - Data Profile",
            explorative=True,  # Show correlations and interactions
            minimal=False,     # Show full details (we want the "wow" factor)
        )
        
        # Generate the HTML
        html_report = profile.to_html()
        
        return html_report
        
    except ImportError:
        return """
        <div style="padding: 20px; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px;">
            <h3>⚠️ YData Profiling Not Installed</h3>
            <p>To generate this report, please run:</p>
            <code>pip install ydata-profiling</code>
            <p>Then restart the kernel and try again.</p>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="padding: 20px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px;">
            <h3>❌ Error Generating Profile</h3>
            <p>{str(e)}</p>
        </div>
        """

def get_data_quality_summary(df):
    """
    Returns a quick summary dictionary of data quality issues.
    Useful for the Streamlit dashboard overview.
    """
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": len(df.select_dtypes(include=['number']).columns),
        "text_columns": len(df.select_dtypes(include=['object']).columns),
        "date_columns": len(df.select_dtypes(include=['datetime64']).columns),
    }
    
    # Check for columns with >50% missing
    high_missing = []
    for col in df.columns:
        if df[col].isnull().mean() > 0.5:
            high_missing.append(col)
    summary["columns_with_high_missing"] = high_missing
    
    return summary