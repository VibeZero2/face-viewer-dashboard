#!/usr/bin/env python3
"""
Test script to debug mode switching issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.cleaning import DataCleaner
from config import DATA_DIR

def test_mode_switching():
    print("=== Testing Mode Switching ===")
    
    # Test 1: Create DataCleaner in TEST mode
    print("\n1. Creating DataCleaner in TEST mode...")
    test_cleaner = DataCleaner(str(DATA_DIR), test_mode=True)
    print(f"   test_cleaner.test_mode: {test_cleaner.test_mode}")
    
    # Load data
    test_cleaner.load_data()
    print(f"   After load_data - test_cleaner.test_mode: {test_cleaner.test_mode}")
    print(f"   Raw data length: {len(test_cleaner.raw_data) if test_cleaner.raw_data is not None else 'None'}")
    
    # Test 2: Create DataCleaner in PRODUCTION mode
    print("\n2. Creating DataCleaner in PRODUCTION mode...")
    prod_cleaner = DataCleaner(str(DATA_DIR), test_mode=False)
    print(f"   prod_cleaner.test_mode: {prod_cleaner.test_mode}")
    
    # Load data
    prod_cleaner.load_data()
    print(f"   After load_data - prod_cleaner.test_mode: {prod_cleaner.test_mode}")
    print(f"   Raw data length: {len(prod_cleaner.raw_data) if prod_cleaner.raw_data is not None else 'None'}")
    
    # Test 3: Check data summary
    print("\n3. Testing data summaries...")
    test_summary = test_cleaner.get_data_summary()
    prod_summary = prod_cleaner.get_data_summary()
    
    print(f"   Test mode summary: {test_summary}")
    print(f"   Production mode summary: {prod_summary}")
    
    # Test 4: Check cleaned data
    print("\n4. Testing cleaned data...")
    test_cleaner.standardize_data()
    test_cleaner.apply_exclusion_rules()
    test_cleaned = test_cleaner.get_cleaned_data()
    
    prod_cleaner.standardize_data()
    prod_cleaner.apply_exclusion_rules()
    prod_cleaned = prod_cleaner.get_cleaned_data()
    
    print(f"   Test cleaned data length: {len(test_cleaned)}")
    print(f"   Production cleaned data length: {len(prod_cleaned)}")
    
    if len(test_cleaned) > 0:
        test_participants = test_cleaned['pid'].nunique()
        print(f"   Test mode participants: {test_participants}")
    
    if len(prod_cleaned) > 0:
        prod_participants = prod_cleaned['pid'].nunique()
        print(f"   Production mode participants: {prod_participants}")

if __name__ == "__main__":
    test_mode_switching()
