"""
Reshapers Module
Handles reshaping data into tidy long format based on detected shape type.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import re
import logging

logging.basicConfig(level=logging.INFO)

def reshape_to_panel_format(df: pd.DataFrame, shape_type: str, filename: str) -> pd.DataFrame:
    """
    Main entry: reshape any supported shape type to panel format (one row per entity-period, one column per variable).
    """
    if df.empty:
        return df
    shape_type = (shape_type or '').lower()
    if shape_type == 'wide':
        return _reshape_wide_to_panel(df, filename)
    elif shape_type == 'two_row_header':
        return _reshape_two_row_header_to_panel(df, filename)
    elif shape_type == 'key_value':
        return _reshape_key_value_to_panel(df, filename)
    elif shape_type == 'cross_tab':
        return _reshape_cross_tab_to_panel(df, filename)
    elif shape_type == 'fully_transposed':
        return _reshape_fully_transposed_to_panel(df, filename)
    elif shape_type == 'stacked_multi_time_long':
        return _reshape_stacked_multi_time_long_to_panel(df, filename)
    elif shape_type == 'pivoted_by_variable':
        return _reshape_pivoted_by_variable_to_panel(df, filename)
    else:
        logging.warning(f"Unknown or unsupported shape_type '{shape_type}', returning DataFrame as-is.")
        return df

def extract_var_period_dynamic(col):
    logging.info(f"[Reshaper] Extracting variable and period from column name: {col}")
    # Look for a 4-digit year (including negative), 2-4 digit year, Q+digit, or month name anywhere in the string
    period_regex = r'(?:-?\d{4}Q\d|Q\d-?\d{4}|-?\d{4}|-?\d{2,4}|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)'
    m = re.search(period_regex, col, re.IGNORECASE)
    if m:
        period = m.group(0)
        prefix = col[:m.start()] + col[m.end():]
        prefix = prefix.strip("_- ")
        return prefix, period
        
    return col, None



def _reshape_wide_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Fully dynamic wide-to-tidy-panel function:
    - Identifies static columns (those for which extract_var_period_dynamic returns period=None)
    - Melts all other columns
    - Extracts variable and period from each column name
    - Pivots to tidy panel format (one row per entity-period, one column per variable)
    """
    logging.info(f"[Reshaper] Processing wide format from: {filename}")
    if df.empty:
        return df
    static_cols = [col for col in df.columns if extract_var_period_dynamic(col)[1] is None]
    value_cols = [col for col in df.columns if col not in static_cols]
    long_df = df.melt(id_vars=static_cols, value_vars=value_cols, var_name='orig_col', value_name='value')
    long_df[['variable', 'period']] = long_df['orig_col'].apply(lambda x: pd.Series(extract_var_period_dynamic(x)))
    index_cols = [col for col in static_cols if col != 'period'] + ['period']
    panel = long_df.pivot_table(index=index_cols, columns='variable', values='value', aggfunc='first').reset_index()
    panel.columns.name = None
    return panel

def _reshape_two_row_header_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Assume first two rows are headers
    logging.info(f"[Reshaper] Processing two_row_header format from: {filename}")
    new_cols = [f"{str(df.iloc[1, i])}_{str(df.iloc[0, i])}" for i in range(df.shape[1])]
    df2 = df.iloc[2:].copy()
    df2.columns = new_cols
    return _reshape_wide_to_panel(df2, filename)

    
def _reshape_key_value_to_panel(df: pd.DataFrame, filename: str, variable_candidates=None, value_candidates=None) -> pd.DataFrame:
    logging.info("[Reshaper] Processing key_value format (dynamic)")
    if variable_candidates is None:
        variable_candidates = ['variable', 'var', 'name', 'attribute', 'feature', 'measure', 'indicator', 'item']
    if value_candidates is None:
        value_candidates = ['value', 'val', 'amount']
    col_map = {col.lower(): col for col in df.columns}
    variable_col = next((col_map[c] for c in variable_candidates if c in col_map), None)
    value_col = next((col_map[c] for c in value_candidates if c in col_map), None)
    id_cols = [col for col in df.columns if col not in [variable_col, value_col]]
    
    if variable_col and value_col:
        # Pivot from long format to wide panel format
        panel = df.pivot_table(
            index=id_cols,
            columns=variable_col,
            values=value_col,
            aggfunc='first'
        ).reset_index()
        panel.columns.name = None
        return panel
    elif len(df.columns) >= 3:
        id_cols = list(df.columns[:-2])
        key_col, value_col = df.columns[-2:]
        # Pivot from long format to wide panel format
        panel = df.pivot_table(
            index=id_cols,
            columns=key_col,
            values=value_col,
            aggfunc='first'
        ).reset_index()
        panel.columns.name = None
        return panel
    else:
        logging.warning("Key-value fallback: not enough columns to reshape.")
        return df

def _reshape_cross_tab_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Assume first column is row variable, columns are col variable
    logging.info(f"[Reshaper] Processing cross_tab format from: {filename}")
    row_var = df.columns[0]
    col_vars = df.columns[1:]
    long_df = df.melt(id_vars=[row_var], value_vars=col_vars, var_name='col_var', value_name='value')
    # Try to extract period from col_var
    long_df[['variable', 'period']] = long_df['col_var'].apply(lambda x: pd.Series(extract_var_period_dynamic(x)))
    # Pivot to panel
    panel = long_df.pivot_table(index=[row_var, 'period'], columns='variable', values='value', aggfunc='first').reset_index()
    panel.columns.name = None
    return panel

def _reshape_fully_transposed_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Transpose, then treat as wide
    logging.info(f"[Reshaper] Processing fully_transposed format from: {filename}")
    df2 = df.set_index(df.columns[0]).T.reset_index()
    df2.columns = [str(c) for c in df2.columns]
    return _reshape_wide_to_panel(df2, filename)

def _reshape_stacked_multi_time_long_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Already in panel format: just return as is
    logging.info(f"[Reshaper] Processing stacked_multi_time_long format from: {filename}")
    return df.copy()





def _reshape_pivoted_by_variable_to_panel(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Convert a *pivoted-by-variable* table (rows = variables, columns =
    mixed dimension(s)+period) to a tidy panel with **all** identifiers as
    separate columns.

    """
    logging.info(f"[Reshaper] pivoted_by_variable → tidy panel   file: {filename}")

    # 1 ───────────────────────────────────────────────────────── variable column
    delimiter_regex: str = r"[_\-\s]+" # how to split multiple IDs
    variable_names = ['variable', 'var', 'name', 'attribute', 'feature', 'measure', 'indicator', 'item']
    var_col = next((c for c in df.columns if c.lower() in variable_names), df.columns[0])

    # 2 ───────────────────────────────────────────────────────── long form (melt)
    long_df = df.melt(
        id_vars=[var_col],
        value_vars=[c for c in df.columns if c != var_col],
        var_name="orig_header",
        value_name="value",
    )

    # 3 ───────────────────────────────────────────── split header → dims & period
    def _split_header(h: str):
        prefix, period = extract_var_period_dynamic(h)
        dims = re.split(delimiter_regex, prefix) if prefix else []
        return dims, period

    # first pass: how many dimension tokens at most?
    max_dims = 0
    dims_period = []
    for h in long_df["orig_header"]:
        dims, per = _split_header(h)
        dims_period.append((dims, per))
        max_dims = max(max_dims, len(dims))

    # Check if any periods were found
    periods_found = any(per is not None for dims, per in dims_period)
    if not periods_found:
        logging.error(f"[Reshaper] No periods found in any column headers for file: {filename}")
        return df

    dim_cols = [f"dim_{i+1}" for i in range(max_dims)]
    
    # Build records using range to avoid length mismatch issues
    assert len(dims_period) == len(long_df), f"Header parsing mismatch: {len(dims_period)} != {len(long_df)}"
    records = []
    for i in range(len(long_df)):
        dims, per = dims_period[i]
        record = [*(dims + [None]*(max_dims - len(dims))), per]
        records.append(record)
    
    extracted = pd.DataFrame(records, columns=pd.Index(list(dim_cols) + ["period"]))
   
    long_df = long_df.reset_index(drop=True)
    extracted = extracted.reset_index(drop=True)
    long_df = pd.concat([long_df, extracted], axis=1)

    # keep only rows with a detected period
    long_df = long_df[long_df["period"].notnull()]

    # drop dimension columns that are completely empty
    # Line 198 fix  
    dim_cols = [c for c in dim_cols if c in long_df.columns and pd.Series(long_df[c]).notnull().any()]

    # 4 ───────────────────────────────────────────────────── pivot to wide panel
    index_cols = ["period"] + dim_cols
    panel = (
        long_df
        .pivot_table(
            index=index_cols,
            columns=var_col,
            values="value",
            aggfunc="first",
        )
        .reset_index()
    )
    panel.columns.name = None
    return panel