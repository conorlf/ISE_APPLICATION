"""
Audit Reporter Module
Handles comprehensive auditing and reporting of the data harmonization process.
"""

import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime


def generate_audit_report(
    harmonization_decisions: Dict[str, Any],
    cleaning_actions: List[Dict[str, Any]],
    flagged_issues: List[Dict[str, Any]],
    duplicate_summary: Dict[str, Any],
    processing_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a comprehensive audit report with all harmonization decisions,
    cleaning actions, flagged issues, and processing statistics.
    
    Args:
        harmonization_decisions: AI and fallback harmonization mappings
        cleaning_actions: List of cleaning actions performed
        flagged_issues: List of flagged issues/suspicious values
        duplicate_summary: Summary of deduplication process
        processing_stats: General processing statistics
        
    Returns:
        Comprehensive audit report dictionary
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': _generate_summary_section(
            processing_stats, duplicate_summary, flagged_issues
        ),
        'harmonization_decisions': _format_harmonization_decisions(harmonization_decisions),
        'cleaning_actions': _format_cleaning_actions(cleaning_actions),
        'flagged_issues': _format_flagged_issues(flagged_issues),
        'duplicate_analysis': _format_duplicate_analysis(duplicate_summary),
        'processing_statistics': processing_stats
    }
    
    return report


def _generate_summary_section(
    processing_stats: Dict[str, Any],
    duplicate_summary: Dict[str, Any],
    flagged_issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate executive summary section of the audit report.
    """
    total_files = processing_stats.get('total_files_processed', 0)
    total_records = processing_stats.get('total_records_processed', 0)
    duplicate_records = duplicate_summary.get('duplicate_records', 0)
    suspicious_records = sum(issue.get('affected_records', 0) for issue in flagged_issues if issue.get('type') == 'suspicious_value')
    
    summary = {
        'total_files_processed': total_files,
        'total_records_processed': total_records,
        'final_clean_records': total_records - duplicate_records,
        'duplicate_records_removed': duplicate_records,
        'suspicious_records_flagged': suspicious_records,
        'data_quality_score': _calculate_quality_score(
            total_records, duplicate_records, suspicious_records
        ),
        'processing_time_seconds': processing_stats.get('processing_time_seconds', 0),
        'harmonization_confidence': processing_stats.get('avg_harmonization_confidence', 0)
    }
    
    return summary


def _format_harmonization_decisions(harmonization_decisions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format harmonization decisions for the audit report.
    """
    formatted_decisions = []
    
    for original_col, mapping_info in harmonization_decisions.items():
        decision = {
            'original_column': original_col,
            'mapped_column': mapping_info.get('mapped_name', 'unknown'),
            'confidence_score': mapping_info.get('confidence', 0),
            'method_used': mapping_info.get('method', 'unknown'),
            'fallback_used': mapping_info.get('fallback_used', False),
            'ai_reasoning': mapping_info.get('ai_reasoning', ''),
            'sample_values': mapping_info.get('sample_values', [])
        }
        formatted_decisions.append(decision)
    
    return formatted_decisions


def _format_cleaning_actions(cleaning_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format cleaning actions for the audit report.
    """
    formatted_actions = []
    
    for action in cleaning_actions:
        formatted_action = {
            'action_type': action.get('type', 'unknown'),
            'column_affected': action.get('column', 'all'),
            'description': action.get('description', ''),
            'records_affected': action.get('records_affected', 0),
            'old_values': action.get('old_values', []),
            'new_values': action.get('new_values', []),
            'timestamp': action.get('timestamp', datetime.now().isoformat())
        }
        formatted_actions.append(formatted_action)
    
    return formatted_actions


def _format_flagged_issues(flagged_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format flagged issues for the audit report.
    """
    formatted_issues = []
    
    for issue in flagged_issues:
        formatted_issue = {
            'issue_type': issue.get('type', 'unknown'),
            'severity': issue.get('severity', 'medium'),
            'description': issue.get('description', ''),
            'affected_records': issue.get('affected_records', 0),
            'columns_involved': issue.get('columns_involved', []),
            'suggested_action': issue.get('suggested_action', ''),
            'timestamp': issue.get('timestamp', datetime.now().isoformat())
        }
        formatted_issues.append(formatted_issue)
    
    return formatted_issues


def _format_duplicate_analysis(duplicate_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format duplicate analysis for the audit report.
    """
    return {
        'original_records': duplicate_summary.get('original_records', 0),
        'clean_records': duplicate_summary.get('clean_records', 0),
        'duplicate_records': duplicate_summary.get('duplicate_records', 0),
        'duplicate_percentage': duplicate_summary.get('duplicate_percentage', 0),
        'id_columns_used': duplicate_summary.get('id_columns_used', []),
        'time_columns_used': duplicate_summary.get('time_columns_used', []),
        'duplication_patterns': _analyze_duplication_patterns(duplicate_summary)
    }


def _analyze_duplication_patterns(duplicate_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze patterns in the duplicate records.
    """
    patterns = []
    
    # This would be enhanced with actual duplicate analysis
    # For now, return basic pattern information
    patterns.append({
        'pattern_type': 'exact_match',
        'description': 'Records with identical values in all ID and time columns',
        'frequency': duplicate_summary.get('duplicate_records', 0)
    })
    
    return patterns


def _calculate_quality_score(
    total_records: int,
    duplicate_records: int,
    suspicious_records: int
) -> float:
    """
    Calculate a data quality score based on various metrics.
    """
    if total_records == 0:
        return 0.0
    
    # Base score starts at 100
    score = 100.0
    
    # Deduct points for duplicates (up to 20 points)
    duplicate_penalty = min(20, (duplicate_records / total_records) * 100)
    score -= duplicate_penalty
    
    # Deduct points for suspicious records (up to 30 points)
    suspicious_penalty = min(30, (suspicious_records / total_records) * 100)
    score -= suspicious_penalty
    
    return max(0, round(score, 2))


def export_audit_report_to_csv(
    audit_report: Dict[str, Any],
    output_path: str
) -> str:
    """
    Export the audit report to a CSV file.
    
    Args:
        audit_report: The complete audit report
        output_path: Path where to save the CSV file
        
    Returns:
        Path to the exported CSV file
    """
    # Create a summary DataFrame for CSV export
    summary_data = []
    
    # Add summary statistics
    summary = audit_report.get('summary', {})
    for key, value in summary.items():
        summary_data.append({
            'metric': key,
            'value': value,
            'category': 'summary'
        })
    
    # Add harmonization decisions
    for decision in audit_report.get('harmonization_decisions', []):
        summary_data.append({
            'metric': f"Column Mapping: {decision['original_column']} -> {decision['mapped_column']}",
            'value': f"Confidence: {decision['confidence_score']}, Method: {decision['method_used']}",
            'category': 'harmonization'
        })
    
    # Add cleaning actions
    for action in audit_report.get('cleaning_actions', []):
        summary_data.append({
            'metric': f"Cleaning: {action['action_type']} on {action['column_affected']}",
            'value': f"Records affected: {action['records_affected']}",
            'category': 'cleaning'
        })
    
    # Add flagged issues
    for issue in audit_report.get('flagged_issues', []):
        summary_data.append({
            'metric': f"Issue: {issue['issue_type']} ({issue['severity']})",
            'value': f"Affected records: {issue['affected_records']}",
            'category': 'issues'
        })
    
    # Create DataFrame and export
    df = pd.DataFrame(summary_data)
    df.to_csv(output_path, index=False)
    
    return output_path
