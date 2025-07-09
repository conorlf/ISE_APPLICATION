"""
AI Shape Detection Module
Uses OpenAI to detect the format/shape of datasets.
"""

import json
import os
from typing import Dict, Any, Optional
import pandas as pd
from openai import OpenAI


def detect_data_shape(sample_df: pd.DataFrame, api_key: Optional[str] = None) -> str:
    """
    Detect the shape format of a dataset using AI.
    
    Args:
        sample_df: Sample DataFrame (headers + a few rows)
        api_key: OpenAI API key
        
    Returns:
        String indicating the detected format type
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("[ShapeDetection] No API key available, using local fallback")
        return _local_shape_detection(sample_df)
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Prepare the sample data for AI analysis
        sample_info = _prepare_sample_for_ai(sample_df)
        
        # Generate all format descriptions with type: description format
        format_types = [
            'wide', 'two_row_header', 'key_value', 'cross_tab',
            'fully_transposed', 'stacked_multi_time_long', 'pivoted_by_variable', 'unknown'
        ]
        descriptions = [f"{fmt}: {get_shape_description(fmt)}" for fmt in format_types]
        descriptions_text = "\n".join(descriptions)
        
        # Improved AI prompt for shape detection
        prompt = build_shape_detection_prompt(sample_info['columns'], sample_info['sample_data'])

        # Compose the system prompt with type: description format
        system_prompt = (
            "You are an expert in identifying dataset formats. "
            "Your task is to analyze a provided dataset sample and determine its format type. "
            "The possible format types are listed below with their descriptions.\n"
            f"{descriptions_text}\n"
            "The provided dataset sample includes both column information and a data sample. Ensure that these elements are clear and correctly formatted for accurate analysis."
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent detection
            max_tokens=50
        )
        
        # Extract and validate the response
        content = response.choices[0].message.content
        if content is None:
            print("[ShapeDetection] AI returned empty response, using local fallback")
            return _local_shape_detection(sample_df)
        # Robustly extract the first valid format type from the response
        valid_formats = [
            'wide', 'two_row_header', 'key_value', 'cross_tab', 'fully_transposed', 'stacked_multi_time_long', 'pivoted_by_variable', 'unknown'
        ]
        content_lower = content.strip().lower()
        detected_format = None
        for fmt in valid_formats:
            if fmt in content_lower:
                detected_format = fmt
                break
        if detected_format:
            print(f"[ShapeDetection] AI detected format: {detected_format}")
            return detected_format
        else:
            print(f"[ShapeDetection] AI returned invalid format '{content}', using local fallback")
            return _local_shape_detection(sample_df)
            
    except Exception as e:
        print(f"[ShapeDetection] AI detection failed: {e}, using local fallback")
        return _local_shape_detection(sample_df)


def _prepare_sample_for_ai(sample_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepare sample DataFrame for AI analysis.
    
    Args:
        sample_df: Sample DataFrame
        
    Returns:
        Dictionary with columns and sample data for AI prompt
    """
    # Get column information
    columns = list(sample_df.columns)
    
    # Get sample data (first 5 rows, excluding the first row, and do not cap columns)
    sample_data = "\n".join(
        " ".join(str(val) for val in row)
        for row in sample_df.iloc[0:5].values
    )
    
    return {
        'columns': columns,
        'sample_data': sample_data
    }


def _local_shape_detection(sample_df: pd.DataFrame) -> str:
    """
    Local fallback for shape detection using heuristics.
    
    Args:
        sample_df: Sample DataFrame
        
    Returns:
        String indicating the detected format type
    """
    columns = sample_df.columns.tolist()
    
    # Check for classic wide format (revenue_2020, emp_2021)
    if any('_' in col and col.split('_')[-1].isdigit() and len(col.split('_')[-1]) == 4 for col in columns):
        return 'wide'
    
    # Check for wide year prefix (2020_revenue, 2021_emp)
    if any(col.split('_')[0].isdigit() and len(col.split('_')[0]) == 4 for col in columns if '_' in col):
        return 'wide_year_prefix'
    
    # Check for key-value format
    if 'variable' in columns and 'value' in columns:
        return 'key_value'
    
    # Check for stacked multi-year long
    if 'year' in columns:
        return 'stacked_multi_year_long'
    
    # Check for two-row header (look for patterns in first few rows)
    if len(sample_df) >= 2:
        first_row = sample_df.iloc[0].astype(str)
        second_row = sample_df.iloc[1].astype(str)
        # Check if first row contains years and second row contains variables
        if any(year.isdigit() and len(year) == 4 for year in first_row):
            return 'two_row_header'
    
    # Check for cross-tab format (look for categorical columns)
    categorical_cols = [col for col in columns if sample_df[col].dtype == 'object']
    if len(categorical_cols) >= 2:
        # Check if it looks like a cross-tabulation
        unique_counts = [sample_df[col].nunique() for col in categorical_cols[:2]]
        if all(count < 50 for count in unique_counts):  # Reasonable for categories
            return 'cross_tab'
    
    # Check for fully transposed (years in first row)
    if len(sample_df) > 0:
        first_row_values = sample_df.iloc[0].astype(str)
        if any(val.isdigit() and len(val) == 4 for val in first_row_values):
            return 'fully_transposed'
    
    # Check for pivoted by variable (variables as rows)
    if len(columns) <= 5:  # Few columns suggest variables might be in rows
        return 'pivoted_by_variable'
    
    # Default to unknown
    return 'unknown'


def get_shape_description(shape_type: str) -> str:

    descriptions = {
  "wide": "Each time period is part of the column name (e.g., 'Sales_2020'). Rows are entities; columns are time-stamped variables.",
  "two_row_header": "Table has a two-row header: one row for time periods, one for variable names. Combine both rows for full column meaning. Data rows follow.",
  "key_value": "Data is in tidy/key-value format. There is a column (e.g., 'variable') that contains variable names as values, and a column (e.g., 'value') that contains the corresponding values. Each row represents a single variable for a specific entity and time. Variables are not columns.",
  "cross_tab": "Matrix table where two or more categorical variables define rows and columns. Cells contain values. Time is not a column.",
  "fully_transposed": "Time periods are columns. All variables are listed as rows. Metadata is in rows, time in columns.",
  "stacked_multi_time_long": "Each row is an entity at a specific time. Time is in a column (e.g., 'Year'). Each variable (e.g., 'revenue', 'employees', 'sex') is its own column.",
  "pivoted_by_variable": "Each row is a variable. Columns are dimensions like region, time, or category. Variable names are in rows.",
  "unknown": "Table does not match any known pattern or is inconsistent, malformed, or ambiguous."
}
    
    return descriptions.get(shape_type, 'Unknown format')


def build_shape_detection_prompt(columns, sample_data):
    return f"""Return only the format type (as listed above) as a single word, with no explanation, no extra text, and no punctuation.
If the sample does not match any of the listed types, return unknown.
Sample Information:
Columns: {columns}
Data Sample: {sample_data}
"""
