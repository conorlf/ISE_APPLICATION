"""
Test script to verify all modules work correctly.
"""

import pandas as pd
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_modules():
    """Test all the modules to ensure they work correctly."""
    
    print("Testing Data Harmonization Modules...")
    
    # Test 1: Create sample data
    print("\n1. Creating sample data...")
    sample_data = {
        'firm_id': ['F001', 'F002', 'F003'],
        'revenue_2020': [1000000, 2000000, 1500000],
        'revenue_2021': [1100000, 2200000, 1600000],
        'employees_2020': [50, 100, 75],
        'employees_2021': [55, 110, 80]
    }
    df = pd.DataFrame(sample_data)
    print(f"Sample DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    
    # Test 2: Test reshaping
    print("\n2. Testing reshaping...")
    try:
        from local.wrangler.reShaper import reshape_to_tidy_long
        reshaped_df = reshape_to_tidy_long(df, "wide", "test.csv")
        print(f"Reshaped to {len(reshaped_df)} rows and {len(reshaped_df.columns)} columns")
        print("Reshaped columns:", list(reshaped_df.columns))
    except Exception as e:
        print(f"Reshaping failed: {e}")
    
    # Test 3: Test value cleaning
    print("\n3. Testing value cleaning...")
    try:
        from local.wrangler.valueCleaner import clean_master_dataframe
        cleaned_df = clean_master_dataframe(df)
        print(f"Cleaned DataFrame has {len(cleaned_df)} rows")
    except Exception as e:
        print(f"Value cleaning failed: {e}")
    
    # Test 4: Test deduplication
    print("\n4. Testing deduplication...")
    try:
        from local.wrangler.deDuplicater import remove_duplicates
        clean_df, duplicate_df = remove_duplicates(df)
        print(f"Clean records: {len(clean_df)}, Duplicate records: {len(duplicate_df)}")
    except Exception as e:
        print(f"Deduplication failed: {e}")
    
    # Test 5: Test fuzzy matching
    print("\n5. Testing fuzzy matching...")
    try:
        from ai.columnHarmionisation.fuzzyMatching import fuzzy_match_columns
        columns = ['firmid', 'revenue', 'staff_count', 'industry']
        mappings = fuzzy_match_columns(columns)
        print("Fuzzy mappings:", mappings)
    except Exception as e:
        print(f"Fuzzy matching failed: {e}")
    
    # Test 6: Test audit reporting
    print("\n6. Testing audit reporting...")
    try:
        from local.wrangler.auditReporter import generate_audit_report
        audit_report = generate_audit_report(
            harmonization_decisions={},
            cleaning_actions=[],
            flagged_issues=[],
            duplicate_summary={},
            processing_stats={'total_files_processed': 1}
        )
        print("Audit report generated successfully")
        print("Report keys:", list(audit_report.keys()))
    except Exception as e:
        print(f"Audit reporting failed: {e}")
    
    print("\nModule testing completed!")

if __name__ == "__main__":
    test_modules() 