"""
Value Cleaner Module
Handles cleaning and standardization of data values in the merged master DataFrame.
"""

import pandas as pd
import numpy as np
import re
import os
from typing import Dict, Any, List, Tuple

def _transform_abbreviated_numbers(value: str) -> str:
    """
    Transform abbreviated numbers like '10k', '2.5m', '1b' to full numbers.
    
    Args:
        value: String value that might contain abbreviated numbers
        
    Returns:
        Transformed string with full numbers
    """
    original_value = str(value)
    
    # Pattern to match number followed by k/K/m/M/b/B
    pattern = r'(\d+(?:\.\d+)?)\s*([kmb])'
    
    def replace_match(match):
        number = float(match.group(1))
        suffix = match.group(2).lower()
        
        multipliers = {
            'k': 1_000,
            'm': 1_000_000, 
            'b': 1_000_000_000
        }
        
        result = number * multipliers[suffix]
        # Return as integer if it's a whole number, otherwise as float
        transformed = str(int(result)) if result.is_integer() else str(result)
        print(f"[ValueCleaner] Transformed: '{match.group(0)}' -> '{transformed}'")
        return transformed
    
    # Apply transformation case-insensitively
    result = re.sub(pattern, replace_match, original_value, flags=re.IGNORECASE)
    
    # Debug: only print if transformation occurred
    if result != original_value:
        print(f"[ValueCleaner] Full transformation: '{original_value}' -> '{result}'")
    
    return result

def _load_mappings_from_file() -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
    """
    Load direct mappings and pattern mappings from the combined_mappings file.
    
    Returns:
        Tuple of (direct_mappings_dict, pattern_mappings_list)
    """
    # Get the path to the mappings file
    script_dir = os.path.dirname(__file__)
    mappings_file = os.path.join(script_dir, 'combined_mappings.txt')
    
    direct_mappings = {}
    pattern_mappings = []
    
    try:
        with open(mappings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into sections
        sections = content.split('=== Pattern Mappings ===')
        
        if len(sections) >= 1:
            # Parse direct mappings section
            direct_section = sections[0].replace('=== Direct Mappings ===', '').strip()
            for line in direct_section.split('\n'):
                line = line.strip()
                if line and ' -> ' in line:
                    # Parse format: "key" -> "value"
                    parts = line.split(' -> ', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().strip('"')
                        value = parts[1].strip().strip('"')
                        direct_mappings[key] = value
        
        if len(sections) >= 2:
            # Parse pattern mappings section
            pattern_section = sections[1].strip()
            for line in pattern_section.split('\n'):
                line = line.strip()
                if line and ' | ' in line:
                    # Parse format: regex_pattern | replacement | description
                    parts = line.split(' | ')
                    if len(parts) >= 2:
                        pattern = parts[0].strip()
                        replacement = parts[1].strip()
                        # Remove quotes if present
                        if pattern.startswith("r'") and pattern.endswith("'"):
                            pattern = pattern[2:-1]
                        if replacement.startswith("r'") and replacement.endswith("'"):
                            replacement = replacement[2:-1]
                        if replacement.startswith("'") and replacement.endswith("'"):
                            replacement = replacement[1:-1]
                        pattern_mappings.append((pattern, replacement))
    
    except FileNotFoundError:
        print(f"Warning: Mappings file not found at {mappings_file}. Using empty mappings.")
    except Exception as e:
        print(f"Warning: Error loading mappings file: {e}. Using empty mappings.")
    
    return direct_mappings, pattern_mappings


def clean_master_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the merged master DataFrame by applying value mapping rules,
    standardizing codes, handling metadata, and inferring data types.
    
    Args:
        df: Merged master DataFrame to clean
        
    Returns:
        Cleaned DataFrame with standardized values and types
    """
    if df.empty:
        return df
    
    cleaned_df = df.copy()
    
   

    # Apply value mapping rules
   # cleaned_df = _apply_value_mappings(cleaned_df)
    
    # Standardise codes
    cleaned_df = _standardize_codes(cleaned_df)

    # Handle metadata columns
    cleaned_df = _handle_metadata_columns(cleaned_df)
    
    # Infer and standardise data types
    cleaned_df = _infer_and_standardize_types(cleaned_df)
    
    # Strip spaces and ensure all empties are 'NULL'
    cleaned_df = _clean_empty_values(cleaned_df)
    
    return cleaned_df



def _standardize_codes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize codes (e.g., always "Male"/"Female" for gender).
    """
    # Gender standardization
    if 'sex' in df.columns:
        df['sex'] = df['sex'].astype(str).str.strip()
        gender_mapping = {
            'male': 'Male', 'm': 'Male',
            'female': 'Female', 'f': 'Female', 
            'other': 'Other', 
        }
        df['sex'] = df['sex'].str.lower().map(gender_mapping).fillna(df['sex'])
    
    # Numeric standardization - transform abbreviated numbers for all numeric columns
    numeric_columns = ['revenue', 'employees', 'profit', 'expenses', 'assets']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].apply(_transform_abbreviated_numbers)
    
    # Industry/sector standardization
    if 'industry' in df.columns:
        df['industry'] = df['industry'].astype(str).str.strip().str.title()
    
    # Region standardization
    if 'region' in df.columns:
        df['region'] = df['region'].astype(str).str.strip().str.title()
    
    return df

def _apply_value_mappings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply value mapping rules loaded from combined_mappings file.
    Applies both direct mappings and regex pattern mappings.
    """
    # Load mappings from file
    direct_mappings, pattern_mappings = _load_mappings_from_file()
    
    # Apply direct mappings to all columns (convert to string first)
    for col in df.columns:
        df[col] = df[col].astype(str).replace(direct_mappings)
    
    # Apply pattern mappings using regex
    for col in df.columns:
        for pattern, replacement in pattern_mappings:
            try:
                # Apply regex replacement
                df[col] = df[col].astype(str).str.replace(pattern, replacement, regex=True)
            except Exception as e:
                # Skip problematic patterns and continue
                print(f"Warning: Could not apply pattern '{pattern}' to column '{col}': {e}")
                continue
    
    return df




def _handle_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle metadata columns (extract, fill, and remove metadata rows if needed).
    """
    # Identify potential metadata columns
    metadata_indicators = ['note', 'comment', 'description', 'source', 'metadata']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(indicator in col_lower for indicator in metadata_indicators):
            # Check if this column contains mostly metadata
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.1:  # Low uniqueness suggests metadata
                # Extract useful metadata and fill
                df[col] = df[col].fillna('')
    
    return df


def _infer_and_standardize_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer and standardize data types (numeric, date, categorical, etc.).
    """
    for col in df.columns:
        if col in ['firm_id', 'company_id', 'source', 'sex', 'industry', 'region', 'country']:
            # Keep as string (identifier columns)
            continue
        
        if col == 'year':
            # Convert to numeric year
            df[col] = pd.to_numeric(df[col], errors='coerce')
            continue
        
        if col in ['revenue', 'employees', 'profit', 'expenses', 'assets']:
            # Convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
            continue
        
    
    return df


def _clean_empty_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip spaces and ensure all empties are 'NULL'.
    """
    # Strip spaces from string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # Replace empty strings and NaN with empty strings
    df = df.replace(['', 'nan', 'NaN', 'None', 'none'], '')
    df = df.fillna('')
    
    return df



    """
    Flag rows with suspicious or outlier values.
    
    Args:
        df: DataFrame to check for suspicious values
        
    Returns:
        DataFrame with 'suspicious' column added
    """
    df_with_flags = df.copy()
    df_with_flags['suspicious'] = False
    
    # Check for revenue < employees (suspicious) - simplified to avoid type issues
    if 'revenue' in df.columns and 'employees' in df.columns:
        try:
            # Simple check without complex pandas operations
            for idx, row in df.iterrows():
                try:
                    revenue_val = float(row['revenue'])
                    employees_val = float(row['employees'])
                    if revenue_val < employees_val:
                        df_with_flags.loc[idx, 'suspicious'] = True
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
    
    # Check for missing key fields
    key_fields = ['firm_id', 'year', 'revenue', 'employees']
    missing_key_mask = df_with_flags[key_fields].isin(['NULL', '']).any(axis=1)
    df_with_flags.loc[missing_key_mask, 'suspicious'] = True
    
    return df_with_flags
