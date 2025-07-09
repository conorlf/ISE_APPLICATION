"""
Debug script to test the pipeline and identify issues.
"""

import pandas as pd
from io import StringIO
from pipeline import DataHarmonizationPipeline

def debug_pipeline():
    """Debug the pipeline step by step."""
    
    print("Debugging Data Harmonization Pipeline...")
    
    # Create simple test data
    csv_data1 = """firm_id,revenue_2020,revenue_2021,employees_2020,employees_2021
F001,1000000,1100000,50,55
F002,2000000,2200000,100,110"""
    
    csv_data2 = """company_id,sales_2020,sales_2021,staff_count_2020,staff_count_2021
C001,1500000,1600000,75,80
C002,2500000,2600000,125,130"""
    
    # Create file objects
    file1 = StringIO(csv_data1)
    file2 = StringIO(csv_data2)
    
    files = [file1, file2]
    filenames = ['data1.csv', 'data2.csv']
    
    try:
        # Initialize pipeline
        print("1. Initializing pipeline...")
        pipeline = DataHarmonizationPipeline(use_openai=False)
        print("✅ Pipeline initialized")
        
        # Test step by step
        print("\n2. Testing file ingestion...")
        dataframes, sources = pipeline.ingest_files(files, filenames)
        print(f"✅ Ingested {len(dataframes)} files: {sources}")
        
        print("\n3. Testing shape detection...")
        shapes = pipeline.detect_shapes(dataframes, sources)
        print(f"✅ Detected shapes: {shapes}")
        
        print("\n4. Testing reshaping...")
        reshaped_dfs = pipeline.reshape_data(dataframes, shapes, sources)
        print(f"✅ Reshaped {len(reshaped_dfs)} dataframes")
        
        print("\n5. Testing column harmonization...")
        harmonization_mapping = pipeline.harmonize_columns(reshaped_dfs, sources)
        print(f"✅ Harmonized {len(harmonization_mapping)} columns")
        
        print("\n6. Testing apply harmonized names...")
        harmonized_dfs = pipeline.apply_harmonized_names(reshaped_dfs, harmonization_mapping)
        print(f"✅ Applied harmonized names to {len(harmonized_dfs)} dataframes")
        
        print("\n7. Testing add source columns...")
        source_dfs = pipeline.add_source_columns(harmonized_dfs, sources)
        print(f"✅ Added source columns to {len(source_dfs)} dataframes")
        
        print("\n8. Testing merge dataframes...")
        merged_df = pipeline.merge_dataframes(source_dfs)
        print(f"✅ Merged into {len(merged_df)} rows")
        
        print("\n9. Testing clean master dataframe...")
        cleaned_df = pipeline.clean_master_dataframe(merged_df)
        print(f"✅ Cleaned dataframe has {len(cleaned_df)} rows")
        
        print("\n10. Testing remove duplicates...")
        final_df, duplicates_df = pipeline.remove_duplicates(cleaned_df)
        print(f"✅ Final: {len(final_df)} rows, Duplicates: {len(duplicates_df)} rows")
        
        print("\n11. Testing generate audit report...")
        audit_report = pipeline.generate_comprehensive_audit(final_df, duplicates_df, harmonization_mapping)
        print(f"✅ Generated audit report with {len(audit_report)} sections")
        
        print("\n12. Testing export results...")
        output_file = pipeline.export_results(final_df, duplicates_df, audit_report)
        print(f"✅ Exported to {output_file}")
        
        print("\n🎉 All steps completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_pipeline() 