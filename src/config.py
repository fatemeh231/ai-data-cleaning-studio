# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 11:55:34 2026

@author: fatemeh
"""

# src/config.py
# Configuration for AI Data Cleaning Studio

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# YOUR PERSONAL CONTACT INFO (Hardcoded)
# ============================================
CONTACT_EMAIL = "seyedehfatemehhosseininasab2@gmail.com"
CONTACT_TELEGRAM = "@Fateme_Hosseini1294"
LINKEDIN_URL = "https://www.linkedin.com/in/seyedeh-fatemeh-hosseininasab-7320bb322/"
GITHUB_URL = "https://github.com/fatemeh231"

PRODUCT_NAME = "AI Data Cleaning Studio"
COMPANY_NAME = "SEYEDEH FATEMEH HOSSEININASAB"

# ============================================
# DEMO LIMITS
# ============================================
DEMO_ROW_LIMIT = 1000

# ============================================
# FEATURE FLAGS
# ============================================
FEATURES = {
    "date_cleaning": True,
    "text_cleaning": True,
    "numeric_cleaning": True,
    "categorical_cleaning": True,
    "pii_detection": True,
    "pii_masking": False,       # Premium
    "outlier_detection": False, # Premium
    "batch_processing": False,  # Premium
}

# ============================================
# PATHS
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_PATH = os.path.join(BASE_DIR, "output")

os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)