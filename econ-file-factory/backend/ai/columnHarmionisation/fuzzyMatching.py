import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List
import sqlite3
from difflib import get_close_matches

from openai import OpenAI

CACHE_PATH = Path.home() / ".wrangler_schema_cache.sqlite"

CANONICAL_VARS = [
    "firm_id", "company_id", "year", "revenue", "employees", "sex", "industry", "region", "variable", "value"
]


class SchemaCache:
    def __init__(self, path=CACHE_PATH):
        self.conn = sqlite3.connect(path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS mapping (hash TEXT PRIMARY KEY, data TEXT)")

    def get(self, columns: List[str]):
        h = self._hash(columns)
        cur = self.conn.execute("SELECT data FROM mapping WHERE hash=?", (h,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def set(self, columns: List[str], mapping: Dict[str, str]):
        h = self._hash(columns)
        self.conn.execute("INSERT OR REPLACE INTO mapping VALUES (?, ?)", (h, json.dumps(mapping)))
        self.conn.commit()

    @staticmethod
    def _hash(cols: List[str]):
        return hashlib.md5("|".join(sorted(cols)).encode()).hexdigest()


def heuristic_mapping(columns: List[str]) -> Dict[str, str]:
    from ..utils import canonicalize_variable
    return {c: canonicalize_variable(c) for c in columns}


def llm_mapping(columns: List[str], api_key=None) -> Dict[str, str]:
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return heuristic_mapping(columns)
    client = OpenAI(api_key=api_key)
    prompt = (
        "Map each input column to the best canonical name from this list: "
        + ", ".join(CANONICAL_VARS)
        + ".\nRespond as JSON {input: canonical}. Unknown → input.\nColumns: "
        + ", ".join(columns)
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return heuristic_mapping(columns)


def infer_mapping(columns: List[str], api_key=None) -> Dict[str, str]:
    cache = SchemaCache()
    cached = cache.get(columns)
    if cached:
        return cached
    mapping = llm_mapping(columns, api_key=api_key)
    cache.set(columns, mapping)
    return mapping


def fuzzy_match_columns(input_columns: List[str]) -> Dict[str, str]:
    """
    Fuzzy match input columns to standard columns using difflib.
    
    Args:
        input_columns: List of column names to match
        
    Returns:
        Dictionary mapping input_column -> best_match (or 'unknown')
    """
    # Standard canonical columns for economic/business data
    standard_columns = [
        'firm_id', 'company_id', 'company_name', 'year', 'month', 'quarter', 'date',
        'revenue', 'sales', 'employees', 'staff_count', 'industry', 'sector',
        'region', 'country', 'state', 'city', 'gender', 'sex', 'age_group',
        'product', 'service', 'market_share', 'profit', 'expenses', 'assets',
        'liabilities', 'equity', 'source', 'data_source', 'variable', 'value'
    ]
    
    # Synonym dictionary for common variations
    synonym_dict = {
        # Firm/Company identifiers
        'firmid': 'firm_id', 'firm_code': 'firm_id', 'companyid': 'company_id',
        'company_code': 'company_id', 'org_id': 'company_id', 'organization_id': 'company_id',
        'company': 'company_name', 'firm_name': 'company_name', 'organization': 'company_name',
        
        # Time variables
        'yr': 'year', 'yyyy': 'year', 'fiscal_year': 'year', 'fy': 'year',
        'mth': 'month', 'mo': 'month', 'qtr': 'quarter', 'q': 'quarter',
        
        # Financial metrics
        'total_revenue': 'revenue', 'sales_revenue': 'revenue', 'turnover': 'revenue',
        'income': 'revenue', 'gross_sales': 'sales', 'net_sales': 'sales',
        'staff_total': 'employees', 'headcount': 'employees', 'employee_count': 'employees',
        'workforce': 'employees', 'staff': 'employees', 'personnel': 'employees',
        
        # Demographics
        'gender': 'sex', 'sex_gender': 'sex', 'm_f': 'sex',
        'sector': 'industry', 'business_sector': 'industry', 'sic': 'industry',
        'naics': 'industry', 'area': 'region', 'location': 'region',
        'geo': 'region', 'geography': 'region',
        
        # Data source
        'src': 'source', 'data_src': 'source', 'dataset': 'source',
        'file_source': 'source', 'origin': 'source'
    }
    
    mapping = {}
    
    for col in input_columns:
        col_lower = col.lower().strip()
        
        # First check exact synonym matches
        if col_lower in synonym_dict:
            mapping[col] = synonym_dict[col_lower]
            continue
        
        # Then try fuzzy matching with standard columns
        match = get_close_matches(col_lower, standard_columns, n=1, cutoff=0.6)
        if match:
            mapping[col] = match[0]
        else:
            mapping[col] = 'unknown'
    
    return mapping


def get_synonym_dictionary() -> Dict[str, str]:
    """
    Get the complete synonym dictionary for column harmonization.
    
    Returns:
        Dictionary mapping common variations to canonical names
    """
    return {
        # Firm/Company identifiers
        'firmid': 'firm_id', 'firm_code': 'firm_id', 'companyid': 'company_id',
        'company_code': 'company_id', 'org_id': 'company_id', 'organization_id': 'company_id',
        'company': 'company_name', 'firm_name': 'company_name', 'organization': 'company_name',
        
        # Time variables
        'yr': 'year', 'yyyy': 'year', 'fiscal_year': 'year', 'fy': 'year',
        'mth': 'month', 'mo': 'month', 'qtr': 'quarter', 'q': 'quarter',
        
        # Financial metrics
        'total_revenue': 'revenue', 'sales_revenue': 'revenue', 'turnover': 'revenue',
        'income': 'revenue', 'gross_sales': 'sales', 'net_sales': 'sales',
        'staff_total': 'employees', 'headcount': 'employees', 'employee_count': 'employees',
        'workforce': 'employees', 'staff': 'employees', 'personnel': 'employees',
        
        # Demographics
        'gender': 'sex', 'sex_gender': 'sex', 'm_f': 'sex',
        'sector': 'industry', 'business_sector': 'industry', 'sic': 'industry',
        'naics': 'industry', 'area': 'region', 'location': 'region',
        'geo': 'region', 'geography': 'region',
        
        # Data source
        'src': 'source', 'data_src': 'source', 'dataset': 'source',
        'file_source': 'source', 'origin': 'source'
    } 