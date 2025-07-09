# utils.py - helper functions for data wrangling pipeline

# Add your harmonization, cleaning, deduplication functions here 

def fuzzy_match_columns(input_columns, standard_columns):
    """
    Fuzzy match input columns to standard columns using difflib (free alternative).
    Returns a dict mapping input_column -> best_match (or 'unknown').
    """
    from difflib import get_close_matches
    mapping = {}
    for col in input_columns:
        match = get_close_matches(col, standard_columns, n=1, cutoff=0.6)
        mapping[col] = match[0] if match else 'unknown'
    return mapping

# --- OpenAI API semantic matching to a fixed schema ---

def openai_semantic_match_columns(input_columns, standard_columns, api_key=None, model="gpt-4-turbo"):
    """
    Uses OpenAI's API to semantically match input_columns to standard_columns.
    Returns a dict mapping input_column -> best_match (or 'unknown').
    Requires openai package and an API key (set OPENAI_API_KEY env var or pass as argument).
    """
    import os
    from openai import OpenAI
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OpenAI API key must be set as OPENAI_API_KEY or passed as api_key argument.")

    client = OpenAI(api_key=api_key)
    mapping = {}
    # Batch all columns in one prompt for efficiency
    prompt = (
        f"Given the following standard columns: {', '.join(standard_columns)}.\n"
        "For each of the following input columns, respond with the best matching standard column or 'unknown' if none.\n"
        "Input columns: " + ', '.join(input_columns) + ".\n"
        "Respond as a JSON object: {input_column: best_match, ...}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    import json
    content = response.choices[0].message.content
    try:
        mapping = json.loads(content)
    except Exception:
        # fallback: try to parse manually or return all unknown
        mapping = {col: 'unknown' for col in input_columns}
    return mapping

# --- OpenAI API dynamic canonicalization ---

def openai_dynamic_canonicalize_columns(input_columns, api_key=None, model="gpt-4-turbo", batch_size=20):
    """
    Uses OpenAI's API to suggest canonical column names for each input column, dynamically (no predefined schema).
    Returns a dict mapping original column names to canonical names.
    Batches requests for efficiency. Requires openai package and API key.
    """
    import os
    from openai import OpenAI
    import json
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OpenAI API key must be set as OPENAI_API_KEY or passed as api_key argument.")
    
    client = OpenAI(api_key=api_key)
    mapping = {}
    for i in range(0, len(input_columns), batch_size):
        batch = input_columns[i:i+batch_size]
        prompt = (
            "For each of the following column names from a dataset, suggest a clear, general, and canonical column name "
            "that would be appropriate for economic or demographic data analysis. Respond as a JSON object mapping the "
            "original column name to the canonical name. If a column is already canonical, repeat it.\n"
            f"Columns: {', '.join(batch)}.\n"
            "Respond as: {original_column: canonical_column, ...}"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        try:
            batch_mapping = json.loads(content)
        except Exception:
            batch_mapping = {col: col for col in batch}  # fallback: identity mapping
        mapping.update(batch_mapping)
    return mapping

# --- OpenAI API: Infer likely ID and time columns ---
def infer_id_and_time_columns(columns, api_key=None, model="gpt-4-turbo"):
    """
    Use OpenAI to infer which columns are likely to be unique entity identifiers and which are time variables.
    Returns: (list_of_id_columns, list_of_time_columns)
    """
    import os
    from openai import OpenAI
    import json
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OpenAI API key must be set as OPENAI_API_KEY or passed as api_key argument.")
    
    client = OpenAI(api_key=api_key)
    prompt = (
        f"Given the following column names from a dataset: {', '.join(columns)}.\n"
        "Which columns are most likely to be unique entity identifiers (e.g., firm, company, country, region, etc.)?\n"
        "Which columns are most likely to be time variables (e.g., year, month, quarter, date, period, etc.)?\n"
        'Respond as JSON: {"id_columns": [..], "time_columns": [..]}'
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        return result.get("id_columns", []), result.get("time_columns", [])
    except Exception:
        return [], []

# --- Heuristic fallback: Infer likely ID and time columns ---
def heuristic_id_and_time_columns(columns):
    """
    Infer likely ID and time columns using keyword matching heuristics.
    Returns: (list_of_id_columns, list_of_time_columns)
    """
    id_keywords = ['id', 'name', 'code', 'firm', 'company', 'country', 'region', 'entity']
    time_keywords = ['year', 'month', 'quarter', 'date', 'period', 'time', 'week', 'day']
    id_cols = [col for col in columns if any(k in col.lower() for k in id_keywords)]
    time_cols = [col for col in columns if any(k in col.lower() for k in time_keywords)]
    return id_cols, time_cols



import pandas as pd
import numpy as np
import re
# ------------------------------------------------------
# Have it as only a check for format for the reshaping do the reshaping in house, have a function for that
# Have a function for the standardization of the value
def reshape_if_needed(df):
    """
    Checks if a DataFrame is in a 'complex wide' format (e.g., revenue_2020, employees_2020)
    and reshapes it to a long format if necessary.
    Returns the reshaped DataFrame and a boolean indicating if a reshape occurred.
    """
    stubnames = set()
    # Simple regex to find columns like 'word_4digitnumber'
    for col in df.columns:
        match = re.match(r'(.+)_(\d{4})$', col)
        if match:
            stubnames.add(match.group(1))

    if not stubnames:
        return df, False  # No columns to reshape, return original df

    # Identify the ID variables (anything that isn't part of the stubs)
    id_vars = [col for col in df.columns if not any(col.startswith(str(stub)) for stub in stubnames)]
    
    # Use pandas wide_to_long, a powerful tool for this exact scenario
    try:
        long_df = pd.wide_to_long(
            df,
            stubnames=list(stubnames),
            i=id_vars,
            j='year',
            sep='_'
        ).reset_index()
        return long_df, True
    except Exception as e:
        print(f"Failed to reshape complex wide format: {e}")
        return df, False


def standardize_values(df, value_col='value'):
    """
    Standardizes values in a DataFrame column, especially after melting.
    - Handles numeric shorthands (e.g., '10k', '24,000')
    - Standardizes categorical values (e.g., 'F' -> 'Female')
    """
    if value_col not in df.columns:
        return df

    def clean_val(val):
        if pd.isna(val) or val in ['', 'n/a', 'N/A', 'missing', '.']:
            return np.nan
        
        # Ensure value is a string for processing
        s_val = str(val).strip().lower()

        # Handle categorical values first
        if s_val in ['f', 'female']:
            return 'Female'
        if s_val in ['m', 'male']:
            return 'Male'

        # Handle currency/commas for numeric conversion
        s_val = s_val.replace(',', '').replace('$', '')

        # Handle 'k' for thousands
        if s_val.endswith('k'):
            try:
                # Remove 'k' and convert to float, then multiply
                return float(s_val[:-1]) * 1000
            except (ValueError, TypeError):
                pass  # Fallback if conversion fails

        # Final attempt to convert to a number
        try:
            return pd.to_numeric(s_val)
        except (ValueError, TypeError):
            pass # Not a number, return original value
            
        return val # Return original value if no rule applies

    # Apply the cleaning function to the specified value column
    df[value_col] = df[value_col].apply(clean_val)
    return df


# Example usage:
# input_cols = ['sex', 'gender', 'Firm Identifier', 'Yr', 'Total Revenue', 'Staff', 'Industry']
# mapping = openai_dynamic_canonicalize_columns(input_cols, api_key='sk-...')
# print(mapping)

# ------------------------------------------------------
# Canonicalise variable names with simple heuristics
# ------------------------------------------------------

def canonicalize_variable(var: str) -> str:
    """Return the canonical variable name ('revenue', 'employees', 'sex', etc.)
    based on keywords/prefixes in the supplied string. Used as a last-ditch
    fallback when no explicit mapping exists.
    """
    v = var.lower()
    # Remove common suffixes like _2020, _2021, etc.
    v_no_year = re.sub(r"_\d{4}$", "", v)
    # Core patterns
    if v_no_year in ["revenue", "income", "turnover", "sales"] or v_no_year.startswith("revenue") or v_no_year.startswith("income"):
        return "revenue"
    if v_no_year in ["employees", "staff", "stafftotal", "headcount"] or v_no_year.startswith("employee") or v_no_year.startswith("staff"):
        return "employees"
    if v_no_year in ["sex", "gender", "sexgender"] or v_no_year.startswith("sex") or v_no_year.startswith("gender"):
        return "sex"
    if v_no_year in ["industry", "sector"] or v_no_year.startswith("industry") or v_no_year.startswith("sector"):
        return "industry"
    if v_no_year == "region" or v_no_year.startswith("region"):
        return "region"
    return var  # fallback to original 