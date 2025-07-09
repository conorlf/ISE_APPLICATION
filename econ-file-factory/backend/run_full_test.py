import pandas as pd
from normalize_and_merge import normalize_and_merge

def run_sample_test():
    """
    Runs the full normalization and merge pipeline on the provided sample datasets
    and compares the output to the expected result.
    """
    print("=== RUNNING FULL SAMPLE DATASET TEST ===\n")

    # Define file paths
    files_to_process = [
        ('sampleset1.csv', 'dataset_a'),
        ('sampleset2.csv', 'dataset_b'),
        ('sampleset3.csv', 'dataset_c'),
        ('sampleset4.csv', 'dataset_d'),
    ]
    
    # Load dataframes
    dataframes = []
    sources = []
    for path, src_name in files_to_process:
        try:
            df = pd.read_csv(path)
            dataframes.append(df)
            sources.append(src_name)
            print(f"✅ Loaded {path}")
        except FileNotFoundError:
            print(f"❌ ERROR: Cannot find sample file {path}. Please make sure it's in the root directory.")
            return

    # Run the main function (with AI disabled to test core logic)
    print("\n🚀 Running normalization and merge pipeline...")
    result = normalize_and_merge(dataframes, sources, use_openai=False)
    
    # Unpack results
    master_clean, dupes, missing_report = result
    
    print("\n\n=== PIPELINE FINISHED ===\n")
    print("Cleaned Data Output:")
    print(master_clean.to_string())

    print("\nDuplicate Records Found:")
    print(dupes.to_string())

    print("\nMissing Data Report:")
    print(missing_report)

    # Optional: Save to a file for comparison
    output_filename = "GeneratedOutput.csv"
    master_clean.to_csv(output_filename, index=False)
    print(f"\n✅ Output saved to {output_filename}")
    
    # Compare with expected output
    try:
        expected_df = pd.read_csv("ExpectedOutput.csv", keep_default_na=False, na_values=[''])
        # Convert all to string for comparison to avoid type issues (e.g., 25000 vs 25000.0)
        generated_df = master_clean.astype(str)
        expected_df = expected_df.astype(str)

        # Sort both dataframes to ensure consistent comparison
        generated_df = generated_df.sort_values(by=['firm_id', 'year']).reset_index(drop=True)
        expected_df = expected_df.sort_values(by=['firm_id', 'year']).reset_index(drop=True)
        
        # We only compare the data rows, not the "Duplicate Records" trailer
        expected_df = expected_df.loc[expected_df['firm_id'] != 'Duplicate Records'].dropna(how='all')

        if generated_df.equals(expected_df):
            print("\n\n✅✅✅ SUCCESS: The generated output matches the expected output!")
        else:
            print("\n\n❌❌❌ FAILURE: The generated output does NOT match the expected output.")
            # Show differences using pandas compare
            comparison = generated_df.compare(expected_df, align_axis=0)
            print("Differences found (self=generated, other=expected):")
            print(comparison.to_string())

    except FileNotFoundError:
        print("\n⚠️ Skipping comparison: ExpectedOutput.csv not found.")
    except Exception as e:
        print(f"\n❌ An error occurred during comparison: {e}")

if __name__ == "__main__":
    run_sample_test() 