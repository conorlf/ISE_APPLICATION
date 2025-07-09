"""
Deduplicator Module
Handles removal of true duplicates based on unique identifier variables.
"""

import pandas as pd
from typing import List, Tuple, Dict, Any, cast
from .reShaper import extract_var_period_dynamic


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Remove true duplicates by unique identifier variables and time keys.
    Keep the first occurrence; move extras to a "Duplicate Records" block.
    
    Args:
        df: DataFrame to deduplicate
        
    Returns:
        Tuple of (clean_dataframe, duplicate_records_dataframe)
    """
    if df.empty:
        return df, pd.DataFrame()
    
    # Identify unique identifier variables and time columns
    id_columns, time_columns = _identify_id_columns(df)
    
    if not id_columns:
        # No ID columns found, return original data
        return df, pd.DataFrame()
    
    # Combine ID and time columns for duplicate detection
    duplicate_check_columns = id_columns + time_columns
    
    # Find duplicates
    duplicates_mask = df.duplicated(subset=duplicate_check_columns, keep='first')
    
    # Split into clean and duplicate records
    clean_df = cast(pd.DataFrame, df[~duplicates_mask].copy())
    duplicate_df = cast(pd.DataFrame, df[duplicates_mask].copy())
    
    return clean_df, duplicate_df


def _identify_id_columns(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Identify unique identifier columns by checking first row data values for period information.
    Uses extract_var_period_dynamic on first row to find period column index.
    All columns from index 0 up to and including period column are used as unique identifier.
    If no period column found, use just the first column.
    
    Returns:
        Tuple of (id_columns, time_columns)
    """
    if df.empty:
        return [], []
    
    period_column_index = None
    
    # Check first row values to find period column index
    for col_index, col_name in enumerate(df.columns):
        first_row_value = str(df.iloc[0, col_index]) if len(df) > 0 else ""
        prefix, period = extract_var_period_dynamic(first_row_value)
        print(f"[Deduplicator] Column {col_index} ({col_name}): value='{first_row_value}' -> prefix='{prefix}', period='{period}'")
        
        if period is not None:
            # Found period column - this is our cutoff
            period_column_index = col_index
            print(f"[Deduplicator] Found period column at index {col_index}")
            break
    
    # Determine ID columns based on period column index
    if period_column_index is not None:
        # Use columns 0 through period_column_index (inclusive) as unique identifier
        id_columns = [str(df.columns[i]) for i in range(period_column_index + 1)]
        time_columns = [str(df.columns[period_column_index])]
        print(f"[Deduplicator] Using ID columns: {id_columns} (period found at index {period_column_index})")
    else:
        # No period column found, use just the first column
        id_columns = [str(df.columns[0])] if len(df.columns) > 0 else []
        time_columns = []
        print(f"[Deduplicator] No period column found, using ID columns: {id_columns}")
    
    print(f"[Deduplicator] Final duplicate check will use columns: {id_columns + time_columns}")
    return id_columns, time_columns


def get_duplicate_summary(clean_df: pd.DataFrame, duplicate_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a summary of the deduplication process.
    
    Args:
        clean_df: Clean DataFrame after deduplication
        duplicate_df: DataFrame containing duplicate records
        
    Returns:
        Dictionary with deduplication summary
    """
    if not clean_df.empty:
        id_columns, time_columns = _identify_id_columns(clean_df)
    else:
        id_columns, time_columns = [], []
    
    summary = {
        'original_records': len(clean_df) + len(duplicate_df),
        'clean_records': len(clean_df),
        'duplicate_records': len(duplicate_df),
        'duplicate_percentage': round((len(duplicate_df) / (len(clean_df) + len(duplicate_df))) * 100, 2) if (len(clean_df) + len(duplicate_df)) > 0 else 0,
        'id_columns_used': id_columns,
        'time_columns_used': time_columns
    }
    
    return summary
