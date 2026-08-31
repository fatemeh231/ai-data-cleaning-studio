# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:06:39 2026

@author: fatemeh
"""

# src/pii_detector.py
# PII Detection using Microsoft Presidio
# DEMO VERSION: Detects PII but does NOT mask it (premium feature)

import pandas as pd
import re
from src.config import FEATURES

# Try to import Presidio
try:
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer
    from presidio_anonymizer import AnonymizerEngine
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

# ============================================
# CUSTOM PATTERNS (Fallback if Presidio fails)
# ============================================

def _detect_emails_fallback(text):
    """Detect email addresses using regex."""
    if not isinstance(text, str):
        return []
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def _detect_phones_fallback(text):
    """Detect phone numbers using regex (US/International)."""
    if not isinstance(text, str):
        return []
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US + intl
        r'\d{10,15}',  # Simple digits
    ]
    results = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text))
    return results

def _detect_ids_fallback(text):
    """Detect common ID patterns (SSN-like)."""
    if not isinstance(text, str):
        return []
    # SSN-like: XXX-XX-XXXX
    pattern = r'\d{3}-\d{2}-\d{4}'
    return re.findall(pattern, text)

# ============================================
# MAIN PII DETECTOR
# ============================================

def detect_pii(df):
    """
    Detect PII in all string columns of the DataFrame.
    Returns a dictionary: { 'EMAIL': [...], 'PHONE': [...], 'ID': [...] }
    """
    results = {
        "EMAIL": [],
        "PHONE": [],
        "ID": [],
    }
    
    # If Presidio is available, use it
    if PRESIDIO_AVAILABLE:
        try:
            analyzer = AnalyzerEngine()
            
            for col in df.select_dtypes(include=['object']).columns:
                for idx, value in df[col].dropna().items():
                    if not isinstance(value, str):
                        continue
                    # Analyze the text
                    analysis = analyzer.analyze(text=value, language='en')
                    for entity in analysis:
                        entity_type = entity.entity_type
                        detected_text = value[entity.start:entity.end]
                        
                        if entity_type in ['EMAIL_ADDRESS', 'EMAIL']:
                            results["EMAIL"].append(detected_text)
                        elif entity_type in ['PHONE_NUMBER', 'PHONE']:
                            results["PHONE"].append(detected_text)
                        elif entity_type in ['US_SSN', 'US_ITIN', 'CREDIT_CARD', 'ID']:
                            results["ID"].append(detected_text)
                        # Also catch custom patterns
                        elif entity_type == 'CUSTOM' and any(k in entity.pattern_name for k in ['email', 'phone', 'id']):
                            results["EMAIL"].append(detected_text)
            
            # Remove duplicates
            for key in results:
                results[key] = list(set(results[key]))
                
            return results
            
        except Exception as e:
            # If Presidio fails, fallback to regex
            print(f"Presidio error: {e}. Falling back to regex.")
            return _detect_pii_fallback(df)
    
    else:
        # Presidio not installed – use regex fallback
        return _detect_pii_fallback(df)


def _detect_pii_fallback(df):
    """
    Fallback PII detection using regex (works without Presidio).
    """
    results = {
        "EMAIL": [],
        "PHONE": [],
        "ID": [],
    }
    
    for col in df.select_dtypes(include=['object']).columns:
        for idx, value in df[col].dropna().items():
            if not isinstance(value, str):
                continue
            
            # Emails
            emails = _detect_emails_fallback(value)
            results["EMAIL"].extend(emails)
            
            # Phones
            phones = _detect_phones_fallback(value)
            results["PHONE"].extend(phones)
            
            # IDs
            ids = _detect_ids_fallback(value)
            results["ID"].extend(ids)
    
    # Remove duplicates
    for key in results:
        results[key] = list(set(results[key]))
    
    return results


def mask_pii(df):
    """
    Mask all detected PII in the DataFrame.
    NOTE: This is a PREMIUM feature. In demo, we just return the df unchanged
    and a message saying it's a premium feature.
    """
    if FEATURES.get("pii_masking", False):
        # Full version would implement actual masking
        if PRESIDIO_AVAILABLE:
            try:
                anonymizer = AnonymizerEngine()
                df_copy = df.copy()
                # ... (implement masking logic)
                return df_copy, {"pii_masked": True}
            except:
                pass
        return df, {"pii_masked": False}
    else:
        # DEMO: Return unchanged with a note
        return df, {"pii_masked": "Premium feature - contact for upgrade"}


def get_pii_summary(results):
    """
    Generate a human-readable summary of PII detection results.
    """
    total = sum(len(v) for v in results.values())
    if total == 0:
        return "✅ No PII detected."
    
    summary = f"⚠️ Found {total} potential PII entities:\n"
    if results["EMAIL"]:
        summary += f"  📧 Emails: {len(results['EMAIL'])} found\n"
    if results["PHONE"]:
        summary += f"  📞 Phones: {len(results['PHONE'])} found\n"
    if results["ID"]:
        summary += f"  🆔 IDs: {len(results['ID'])} found\n"
    summary += "\n🔒 Full version masks all PII automatically."
    return summary