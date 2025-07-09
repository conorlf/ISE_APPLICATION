"""
File Readers Module
Handles reading different file formats (.csv, .xlsx, .zip) for data ingestion.
"""

import pandas as pd
import zipfile
import os
from typing import Dict, List, Tuple, Any
from pathlib import Path


def read_file(file_path: str, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Read a file and return the DataFrame along with metadata.
    
    Args:
        file_path: Path to the file
        filename: Original filename
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    file_extension = Path(filename).suffix.lower()
    
    if file_extension == '.csv':
        return _read_csv_file(file_path, filename)
    elif file_extension == '.xlsx':
        return _read_excel_file(file_path, filename)
    elif file_extension == '.zip':
        return _read_zip_file(file_path, filename)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def _read_csv_file(file_path: str, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Read a CSV file.
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError(f"Could not read CSV file with any encoding: {filename}")
        
        metadata = {
            'filename': filename,
            'file_type': 'csv',
            'encoding': encoding,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns)
        }
        
        return df, metadata
        
    except Exception as e:
        raise ValueError(f"Error reading CSV file {filename}: {str(e)}")


def _read_excel_file(file_path: str, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Read an Excel file.
    """
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # Use the first sheet by default
        df = pd.read_excel(file_path, sheet_name=sheet_names[0])
        
        metadata = {
            'filename': filename,
            'file_type': 'excel',
            'sheets': sheet_names,
            'sheet_used': sheet_names[0],
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns)
        }
        
        return df, metadata
        
    except Exception as e:
        raise ValueError(f"Error reading Excel file {filename}: {str(e)}")


def _read_zip_file(file_path: str, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Read a ZIP file containing data files.
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # List all files in the ZIP
            file_list = zip_ref.namelist()
            
            # Find data files (CSV or Excel)
            data_files = [
                f for f in file_list 
                if f.lower().endswith(('.csv', '.xlsx', '.xls'))
            ]
            
            if not data_files:
                raise ValueError(f"No data files found in ZIP: {filename}")
            
            # Use the first data file
            first_data_file = data_files[0]
            
            # Extract and read the file
            with zip_ref.open(first_data_file) as file:
                if first_data_file.lower().endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
            
            metadata = {
                'filename': filename,
                'file_type': 'zip',
                'zip_contents': file_list,
                'data_file_used': first_data_file,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
            
            return df, metadata
            
    except Exception as e:
        raise ValueError(f"Error reading ZIP file {filename}: {str(e)}")


def extract_sample_for_ai(df: pd.DataFrame, sample_size: int = 5) -> pd.DataFrame:
    """
    Extract a sample from the DataFrame for AI processing.
    Includes headers and a few rows.
    
    Args:
        df: DataFrame to sample
        sample_size: Number of rows to include in sample
        
    Returns:
        Sample DataFrame with headers and sample rows
    """
    if df.empty:
        return df
    
    # Take the first few rows
    sample_rows = min(sample_size, len(df))
    sample_df = df.head(sample_rows).copy()
    
    return sample_df


def get_file_info(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Get basic file information without reading the entire file.
    
    Args:
        file_path: Path to the file
        filename: Original filename
        
    Returns:
        Dictionary with file information
    """
    file_info = {
        'filename': filename,
        'file_size_bytes': os.path.getsize(file_path),
        'file_extension': Path(filename).suffix.lower(),
        'file_path': file_path
    }
    
    # Try to get basic info about the data structure
    try:
        if file_info['file_extension'] == '.csv':
            # Read just the header
            df_sample = pd.read_csv(file_path, nrows=0)
            file_info['columns'] = list(df_sample.columns)
            file_info['column_count'] = len(df_sample.columns)
            
        elif file_info['file_extension'] == '.xlsx':
            # Get sheet names
            excel_file = pd.ExcelFile(file_path)
            file_info['sheets'] = excel_file.sheet_names
            file_info['sheet_count'] = len(excel_file.sheet_names)
            
            # Get info from first sheet
            df_sample = pd.read_excel(file_path, sheet_name=excel_file.sheet_names[0], nrows=0)
            file_info['columns'] = list(df_sample.columns)
            file_info['column_count'] = len(df_sample.columns)
            
        elif file_info['file_extension'] == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_info['zip_contents'] = zip_ref.namelist()
                file_info['file_count'] = len(zip_ref.namelist())
                
    except Exception as e:
        file_info['error'] = str(e)
    
    return file_info 