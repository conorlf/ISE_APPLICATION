"""
Data Harmonization Pipeline - Main Orchestrator
Implements the complete Data Harmonization Flow with 11 steps.
"""
import sys
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import os
import io
import zipfile
from werkzeug.utils import secure_filename
import tempfile
import shutil

# Import modular components
from ai.shapeDetection import detect_data_shape
from ai.columnHarmionisation.ai_harmonizer import harmonize_columns
from ai.columnHarmionisation.fuzzyMatching import fuzzy_match_columns, get_synonym_dictionary
from local.ingest.readers import read_file, extract_sample_for_ai
from local.wrangler.reShaper import reshape_to_panel_format
from local.wrangler.valueCleaner import clean_master_dataframe
from local.wrangler.deDuplicater import remove_duplicates, get_duplicate_summary
from local.wrangler.auditReporter import generate_audit_report, export_audit_report_to_csv

class DataHarmonizationPipeline:
    """
    Main orchestrator for the Data Harmonization Flow.
    Implements all 11 steps of the harmonization process.
    """
    def __init__(self, api_key: Optional[str] = None, use_openai: bool = True):
        self.use_openai = use_openai
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.processing_stats = {
            'total_files_processed': 0,
            'total_records_processed': 0,
            'processing_time_seconds': 0,
            'avg_harmonization_confidence': 0
        }
        self.audit_trail = {
            'files_processed': [],
            'shape_detections': [],
            'harmonization_decisions': [],
            'cleaning_actions': [],
            'duplicates_found': [],
            'issues_flagged': []
        }

    def run(self, files: List[Any], filenames: List[str]) -> Dict[str, Any]:
        try:
            # 1. File Upload & Ingestion
            dataframes, sources = self.ingest_files(files, filenames)
            # 2. Shape Detection (AI)
            shapes = self.detect_shapes(dataframes, sources)
           
           
            # 3. Local Reshaping
            reshaped_dfs = self.reshape_data(dataframes, shapes, sources)
         
            # 4. Column Harmonization (AI + Fallback)
            harmonization_mapping = self.harmonize_columns(reshaped_dfs, sources)
            # 5. Apply Harmonized Names
            harmonized_dfs = self.apply_harmonized_names(reshaped_dfs, harmonization_mapping)
            # 6. Add Source Column
            source_dfs = self.add_source_columns(harmonized_dfs, sources)
            # 7. Merge All DataFrames
            merged_df = self.merge_dataframes(source_dfs)
            # 8. Clean the Merged Master DataFrame
            cleaned_df = self.clean_master_dataframe(merged_df)
            # 9. Remove True Duplicates
            final_df, duplicates_df = self.remove_duplicates(cleaned_df)
            # 10. Auditing and Reporting
            audit_report = self.generate_comprehensive_audit(final_df, duplicates_df, harmonization_mapping)
            # 11. Export Results
            output_file = self.export_results(final_df, duplicates_df, audit_report)
            return {
                'master_df': final_df,
                'duplicates_df': duplicates_df,
                'audit_report': audit_report,
                'output_file': output_file,
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'audit_trail': self.audit_trail
            }

    def ingest_files(self, files: List[Any], filenames: List[str]) -> Tuple[List[pd.DataFrame], List[str]]:
        dataframes = []
        sources = []
        
        for file_obj, filename in zip(files, filenames):
            try:
                # Extract files if it's a ZIP
                if filename.endswith('.zip'):
                    extracted_files = self._extract_zip_files(file_obj)
                    for extracted_name, extracted_stream in extracted_files:
                        # Write BytesIO to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=extracted_name[-4:]) as tmp_file:
                            tmp_file.write(extracted_stream.read())
                            tmp_file_path = tmp_file.name
                        try:
                            df, metadata = read_file(tmp_file_path, extracted_name)
                            if df is not None:
                                dataframes.append(df)
                                sources.append(extracted_name)
                        finally:
                            # Clean up temp file
                            os.remove(tmp_file_path)
                else:
                    # Single file
                    df, metadata = read_file(file_obj, filename)
                    if df is not None:
                        dataframes.append(df)
                        sources.append(filename)
                        
            except Exception as e:
                print(f"[Pipeline] Error reading file {filename}: {e}")
                continue
        
        # Update audit trail
        self.audit_trail['files_processed'] = [
            {'filename': src, 'rows': len(df), 'columns': len(df.columns)}
            for df, src in zip(dataframes, sources)
        ]
        
        return dataframes, sources
    
    def detect_shapes(self, dataframes: List[pd.DataFrame], sources: List[str]) -> List[str]:
        """
        Step 2: Shape Detection (AI)
        Extract sample and send to OpenAI for format detection.
        """
        shapes = []
        
        for df, source in zip(dataframes, sources):
            try:
                # Extract sample (headers + a few rows)
                sample_df = df.head(5)  # First 5 rows for context
                
                if self.use_openai and self.api_key:
                    # Send to AI for shape detection
                    shape = detect_data_shape(sample_df, self.api_key)
                else:
                    # Fallback to local detection
                    shape = self._local_shape_detection(sample_df)
                
                shapes.append(shape)
                
                # Update audit trail
                self.audit_trail['shape_detections'].append({
                    'source': source,
                    'detected_shape': shape,
                    'sample_rows': len(sample_df)
                })
                
            except Exception as e:
                print(f"[Pipeline] Error detecting shape for {source}: {e}")
                shapes.append('unknown')  # Default fallback
        
        return shapes
    
    def reshape_data(self, dataframes: List[pd.DataFrame], shapes: List[str], sources: List[str]) -> List[pd.DataFrame]:
        """
        Step 3: Local Reshaping
        Use detected type to reshape data into panel format.
        """
        reshaped_dfs = []
        for df, shape, source in zip(dataframes, shapes, sources):
            try:
                # Reshape based on detected format
                reshaped_df = reshape_to_panel_format(df, shape, source)
                reshaped_dfs.append(reshaped_df)
                
                # Detailed printing for testing
                print(f"\n{'='*60}")
                print(f"RESHAPE TESTING - File: {source}")
                print(f"{'='*60}")
                print(f"Original shape: {df.shape} (rows: {len(df)}, cols: {len(df.columns)})")
                print(f"Detected format: {shape}")
                print(f"Reshaped shape: {reshaped_df.shape} (rows: {len(reshaped_df)}, cols: {len(reshaped_df.columns)})")
                print(f"\nOriginal columns: {list(df.columns)}")
                print(f"Reshaped columns: {list(reshaped_df.columns)}")
                print(f"\nFirst 5 rows of reshaped data:")
                print(reshaped_df.head())
                print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"[Pipeline] Error reshaping {source}: {e}")
                # Keep original if reshaping fails
                reshaped_dfs.append(df)
        
        return reshaped_dfs
      
    def harmonize_columns(self, dataframes: List[pd.DataFrame], sources: List[str]) -> Dict[str, str]:
        """
        Step 4: Column Harmonization (AI + Fallback)
        Collect all unique column names and harmonize them.
        """
        # Collect all unique column names
        all_columns = set()
        for df in dataframes:
            all_columns.update(df.columns)
        
        all_columns = list(all_columns)
        print(f"[Pipeline] Found {len(all_columns)} unique columns to harmonize")
        
        # Extract sample data for context (first few rows from each dataframe)
        sample_data = {}
        for df, source in zip(dataframes, sources):
            # Only extract sample data for columns that exist in this dataframe AND are in all_columns
            for col in all_columns:
                if col in df.columns:  # Check if column exists in this dataframe
                    if col not in sample_data:
                        sample_data[col] = []
                    # Take first 2 non-null values from this column
                    non_null_values = df[col].dropna().head(2).tolist()
                    sample_data[col].extend(non_null_values)
        
        # Limit to first 2 values per column to keep prompt manageable
        for col in sample_data:
            sample_data[col] = sample_data[col][:2]
        
        
        
        print(f"[Pipeline] Extracted sample data for {len(sample_data)} columns")
        
        # 4.1. Context-Aware Harmonization (AI)
        ai_mappings = {}
        if self.use_openai and self.api_key:
            try:
                context = f"economic/business/econometric and financial data from multiple sources."
                ai_mappings = harmonize_columns(all_columns, context=context, api_key=self.api_key, sample_data=sample_data)
                print(f"[Pipeline] AI harmonization completed for {len(ai_mappings)} columns")
            except Exception as e:
                print(f"[Pipeline] AI harmonization failed: {e}")
        
        # 4.2. Receive AI mappings with confidence scores
        final_mapping = {}
        low_confidence_columns = []
        
        for col in all_columns:
            if col in ai_mappings:
                mapping_info = ai_mappings[col]
                canonical_name = mapping_info.get('canonical_name', col)
                confidence = mapping_info.get('confidence', 0.0)
                is_unknown = mapping_info.get('is_unknown', False)
                
                if confidence < 0.7 or is_unknown:
                    low_confidence_columns.append(col)
                    final_mapping[col] = col  # Keep original for now
                else:
                    final_mapping[col] = canonical_name
            else:
                low_confidence_columns.append(col)
                final_mapping[col] = col  # Keep original for now
        
        # 4.3. Fuzzy Matching & Synonym Dictionary Fallback
        if low_confidence_columns:
            print(f"[Pipeline] Applying fallback harmonization to {len(low_confidence_columns)} low-confidence columns")
            fallback_mappings = fuzzy_match_columns(low_confidence_columns)
            
            # 4.4. Merge AI and fallback mappings
            for col in low_confidence_columns:
                if col in fallback_mappings and fallback_mappings[col] != 'unknown':
                    final_mapping[col] = fallback_mappings[col]
        
        # Update audit trail
        self.audit_trail['harmonization_decisions'] = [
            {
                'original': col,
                'mapped_to': final_mapping[col],
                'confidence': ai_mappings.get(col, {}).get('confidence', 0.0) if col in ai_mappings else 0.0,
                'link': ai_mappings.get(col, {}).get('link', col),
                'fallback_used': col in low_confidence_columns
            }
            for col in all_columns
        ]
        
        
        return final_mapping
    
    def apply_harmonized_names(self, dataframes: List[pd.DataFrame], mapping: Dict[str, str]) -> List[pd.DataFrame]:
        """
        Step 5: Apply Harmonized Names
        Rename columns using the final mapping.
        """
        harmonized_dfs = []
        
        for df in dataframes:
            # Create mapping for columns that exist in this DataFrame
            df_mapping = {col: mapping.get(col, col) for col in df.columns}
            
            # Rename columns
            harmonized_df = df.rename(columns=df_mapping)
            harmonized_dfs.append(harmonized_df)
        
        return harmonized_dfs
    
    def add_source_columns(self, dataframes: List[pd.DataFrame], sources: List[str]) -> List[pd.DataFrame]:
        """
        Step 6: Add Source Column to End
        Add source column with filename as the last column.
        """
        source_dfs = []
        
        for df, source in zip(dataframes, sources):
            # Add source column as the last column
            df_with_source = df.copy()
            df_with_source['source'] = source
            source_dfs.append(df_with_source)
        
        return source_dfs
    
    def merge_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Step 7: Merge All DataFrames
        Stack all DataFrames vertically (union columns, fill missing with 'NaN').
        """
        if not dataframes:
            return pd.DataFrame()
        
        # Concatenate all DataFrames vertically
        merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
        
        # Fill missing values with 'NaN'
        merged_df = merged_df.fillna('NaN')
        
        print(f"[Pipeline] Merged {len(dataframes)} DataFrames into {len(merged_df)} rows")
        return merged_df
    
    def clean_master_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 8: Clean the Merged Master DataFrame
        Apply value mapping rules, standardize codes, handle metadata, etc.
        """
        try:
            print(f"[Pipeline] Starting data cleaning for {len(df)} rows, {len(df.columns)} columns")
            cleaned_df = clean_master_dataframe(df)
            print(f"[Pipeline] Data cleaning completed successfully")
            
            # Update audit trail with cleaning actions
            self.audit_trail['cleaning_actions'].append({
                'action': 'master_dataframe_cleaning',
                'rows_processed': len(df),
                'columns_processed': len(df.columns)
            })
            
            return cleaned_df
        except Exception as e:
            print(f"[Pipeline] ERROR in clean_master_dataframe: {e}")
            raise e
    
    def remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Step 9: Remove True Duplicates
        Identify duplicates by firm_id and time key(s).
        """
        try:
            print(f"[Pipeline] Starting duplicate removal for {len(df)} rows")
            final_df, duplicates_df = remove_duplicates(df)
            print(f"[Pipeline] Duplicate removal completed: {len(final_df)} clean records, {len(duplicates_df)} duplicates")
            
            # Update audit trail
            self.audit_trail['duplicates_found'].append({
                'total_records': len(df),
                'duplicate_records': len(duplicates_df),
                'final_records': len(final_df)
            })
            
            return final_df, duplicates_df
        except Exception as e:
            print(f"[Pipeline] ERROR in remove_duplicates: {e}")
            raise e
    
    def generate_comprehensive_audit(self, final_df: pd.DataFrame, duplicates_df: pd.DataFrame, 
                                   harmonization_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Step 10: Comprehensive Auditing and Reporting
        Generate summary report with all harmonization decisions, cleaning actions, etc.
        """
        try:
            print(f"[Pipeline] Starting audit report generation")
            # Prepare audit data
            harmonization_decisions = self._format_harmonization_decisions(harmonization_mapping)
            cleaning_actions = self.audit_trail.get('cleaning_actions', [])
            flagged_issues = self.audit_trail.get('issues_flagged', [])
            
            # Get duplicate summary
            duplicate_summary = get_duplicate_summary(final_df, duplicates_df)
            
            # Generate comprehensive audit report
            audit_report = generate_audit_report(
                harmonization_decisions=harmonization_decisions,
                cleaning_actions=cleaning_actions,
                flagged_issues=flagged_issues,
                duplicate_summary=duplicate_summary,
                processing_stats=self.processing_stats
            )
            print(f"[Pipeline] Audit report generation completed")
            
            return audit_report
        except Exception as e:
            print(f"[Pipeline] ERROR in generate_comprehensive_audit: {e}")
            raise e
    
    def _format_harmonization_decisions(self, harmonization_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Format harmonization decisions for the audit report.
        """
        decisions = {}
        for original_col, mapped_col in harmonization_mapping.items():
            decisions[original_col] = {
                'mapped_name': mapped_col,
                'confidence': 0.8,  # Default confidence for fallback mappings
                'method': 'fuzzy_fallback',
                'fallback_used': True,
                'ai_reasoning': f'Fallback mapping: {original_col} -> {mapped_col}',
                'sample_values': []
            }
        return decisions
    
    def audit_missing_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Step 11: Audit Missing Data
        Count 'NaN' in key fields and issue warnings.
        """
        key_fields = ['firm_id', 'year', 'revenue', 'employees', 'sex']
        missing_counts = {}
        
        for field in key_fields:
            if field in df.columns:
                missing_count = (df[field] == 'NaN').sum()
                missing_counts[field] = missing_count
        
        return missing_counts
    
    def export_results(self, final_df: pd.DataFrame, duplicates_df: pd.DataFrame, 
                      audit_report: Dict[str, Any]) -> str:
        """
        Step 12: Export Results
        Write MASTER.csv file with clean dataset, duplicates, and audit sections.
        """
        try:
            print(f"[Pipeline] Starting results export")
            output_path = 'uploads/MASTER.csv'
            # Ensure the export directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Write clean dataset
                final_df.to_csv(f, index=False, na_rep='')
                
                # Add duplicate records section
                if not duplicates_df.empty:
                    f.write('\n# Duplicate Records\n')
                    duplicates_df.to_csv(f, index=False, na_rep='')
                
                # Add audit sections as comments
                f.write('\n# Audit Report\n')
                f.write(f'# Total records: {len(final_df)}\n')
                f.write(f'# Duplicate records: {len(duplicates_df)}\n')
                f.write(f'# Files processed: {len(self.audit_trail["files_processed"])}\n')
                
                # Add harmonization summary
                if self.audit_trail['harmonization_decisions']:
                    f.write('\n# Harmonization Summary\n')
                    for decision in self.audit_trail['harmonization_decisions']:
                        f.write(f"# {decision['original']} -> {decision['mapped_to']} "
                               f"(confidence: {decision['confidence']:.2f}, "
                               f"fallback: {decision['fallback_used']})\n")
            
            print(f"[Pipeline] Results exported to {output_path}")
            
            return output_path
        except Exception as e:
            print(f"[Pipeline] ERROR in export_results: {e}")
            raise e
    
    def _extract_zip_files(self, zip_file) -> List[Tuple[str, io.BytesIO]]:
        """Extract files from ZIP archive."""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_file) as z:
                for name in z.namelist():
                    if name.endswith(('.csv', '.xlsx')):
                        file_stream = io.BytesIO(z.read(name))
                        extracted_files.append((name, file_stream))
        except Exception as e:
            print(f"[Pipeline] Error extracting ZIP file: {e}")
        return extracted_files
    
    def _local_shape_detection(self, sample_df: pd.DataFrame) -> str:
        """Local fallback for shape detection."""
        # Simple heuristics for shape detection
        columns = sample_df.columns.tolist()
        
        # Check for classic wide format (revenue_2020, emp_2021)
        if any('_' in col and col.split('_')[-1].isdigit() for col in columns):
            return 'wide'
        
        # Check for wide year prefix (2020_revenue, 2021_emp)
        if any(col.split('_')[0].isdigit() for col in columns if '_' in col):
            return 'wide_year_prefix'
        
        # Check for key-value format
        if 'variable' in columns and 'value' in columns:
            return 'key_value'
        
        # Check for stacked multi-year long
        if 'year' in columns:
            return 'stacked_multi_year_long'
        
        # Default to unknown
        return 'unknown' 