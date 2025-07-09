"""
AI-powered column harmonization using OpenAI API with confidence scores.
"""
import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from openai import OpenAI
from datetime import timedelta

class AIHarmonizer:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        """
        Initialize the AI Harmonizer with OpenAI API.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use
        """
        print("[AIHarmonizer] Initializing...")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("[AIHarmonizer] ERROR: No OpenAI API key provided or found in environment.")
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        print(f"[AIHarmonizer] Using OpenAI model: {model}")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

        # Default canonical columns for economic/business data
        self.canonical_columns = ['company_id', 'company_name', 'year', 'month', 'quarter', 'revenue',
         'employees', 'industry', 'country', 'state', 'city', 'gender', 'age_group', 'product', 'service',
          'market_share', 'profit', 'expenses', 'assets', 'liabilities', 'equity','region']

        print(f"[AIHarmonizer] Canonical columns set: {self.canonical_columns}")

        # Static fallback mappings
        self.fallback_mappings = {
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
        print(f"[AIHarmonizer] Fallback mappings loaded ({len(self.fallback_mappings)} entries).")

    def harmonize_columns(self, input_columns: List[str], 
                         context: Optional[str] = None,
                         use_fallback: bool = True,
                         sample_data: Optional[Dict[str, List]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Harmonize input columns to canonical names with confidence scores.
        
        Args:
            input_columns: List of column names to harmonize
            context: Optional context about the data (e.g., "economic survey data")
            use_fallback: Whether to use fallback mappings for API failures
            
        Returns:
            Dictionary mapping each input column to:
            {
                'canonical_name': str,
                'confidence': float (0-1),
                'reasoning': str,
                'link': str,
                'is_unknown': bool
            }
        """
        print(f"[AIHarmonizer] Harmonizing columns: {input_columns}")
        if sample_data:
            print(f"[AIHarmonizer] Using sample data for {len(sample_data)} columns")
        else:
            print("[AIHarmonizer] No sample data provided")
        try:
            # Prepare the prompt
            context_str = f" The data is from {context}." if context else ""
            print(f"[AIHarmonizer] Building system prompt for OpenAI. Context: {context_str}")

            system_prompt = f"""You are a data harmonization expert. Your task is to map input column names to canonical column names with confidence scores.{context_str}

Available canonical columns: {', '.join(self.canonical_columns)}.

For each input column, provide:
1. The best matching canonical name (or suggest a new canonical name if none fit well).
2. A confidence score between 0 and 1.
3. Brief reasoning for the mapping
4. Whether it's unknown (no good match).

IMPORTANT: When multiple input columns represent the same concept (synonyms), assign them ALL to the same canonical name.
For example: 'company_name', 'firm_name', 'organization' should all map to canonical name 'company_name'.

Respond in JSON format."""

           

            user_prompt = f"""Map these columns to canonical names, I have provided accompanying sample data to give context:
{json.dumps(sample_data, indent=2)}

Return a JSON object with this structure:
{{
    "column_name": {{
        "canonical_name": "mapped_name",
        "confidence": 0.95,
        "reasoning": "Direct semantic match",
        "link": "synonyms_of_column_name",
        "is_unknown": false
    }},
    ...
}}

Ensure ALL input columns are included in the response."""

            print("[AIHarmonizer] Sending request to OpenAI API...")
            # Call OpenAI API with structured output
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent mappings
            )
            print("[AIHarmonizer] OpenAI API call completed. Parsing response...")

            # Parse the response
            content = response.choices[0].message.content
            print(f"[AIHarmonizer] Raw OpenAI response: {content}")
            result = json.loads(content or '{}')
            
            # Validate and ensure all columns are mapped
            missing_columns = []
            for col in input_columns:
                if col not in result:
                    print(f"[AIHarmonizer] WARNING: No mapping provided by AI for column '{col}'. Using fallback mapping.")
                    result[col] = {
                        "canonical_name": col,
                        "confidence": 0.5,
                        "reasoning": "No mapping provided by AI - using original column name",
                        "link": col,
                        "is_unknown": True
                    }
                    missing_columns.append(col)
            if missing_columns:
                print(f"[AIHarmonizer] The following columns were missing in AI response and filled with fallback: {missing_columns}")
            
            # Post-process to group synonyms and update link fields
            print("[AIHarmonizer] Post-processing to group synonyms...")
            result = self._group_synonyms(result)
            
            print("[AIHarmonizer] Harmonization complete. Returning result.")
            return result
            
        except Exception as e:
            print(f"[AIHarmonizer] OpenAI API error: {e}")
            
            if use_fallback:
                print("[AIHarmonizer] Using fallback mappings due to error.")
                return self._fallback_harmonization(input_columns)
            else:
                print("[AIHarmonizer] Raising exception due to error and fallback disabled.")
                raise

    def _fallback_harmonization(self, input_columns: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fallback harmonization using static mappings and heuristics.
        """
        print(f"[AIHarmonizer] Performing fallback harmonization for columns: {input_columns}")
        result = {}
        
        for col in input_columns:
            col_lower = col.lower().strip()
            print(f"[AIHarmonizer] Processing column '{col}' (normalized: '{col_lower}')")
            
            # Check static mappings
            if col_lower in self.fallback_mappings:
                print(f"[AIHarmonizer] Found static mapping for '{col_lower}' -> '{self.fallback_mappings[col_lower]}'")
                result[col] = {
                    "canonical_name": self.fallback_mappings[col_lower],
                    "confidence": 0.8,
                    "reasoning": "Matched using fallback dictionary",
                    "link": col,
                    "is_unknown": False
                }
            else:
                # Try fuzzy matching with canonical columns
                best_match = None
                best_score = 0
                print(f"[AIHarmonizer] No static mapping for '{col_lower}'. Trying fuzzy matching...")
                for canonical in self.canonical_columns:
                    # Simple substring matching
                    if col_lower in canonical or canonical in col_lower:
                        score = len(canonical) / max(len(col_lower), len(canonical))
                        print(f"[AIHarmonizer] Fuzzy match candidate: '{canonical}' (score: {score:.2f})")
                        if score > best_score:
                            best_score = score
                            best_match = canonical
                
                if best_match and best_score > 0.6:
                    print(f"[AIHarmonizer] Fuzzy match found: '{col}' -> '{best_match}' (score: {best_score:.2f})")
                    result[col] = {
                        "canonical_name": best_match,
                        "confidence": best_score,
                        "reasoning": f"Fuzzy match with '{best_match}'",
                        "link": col,
                        "is_unknown": False
                    }
                else:
                    print(f"[AIHarmonizer] No suitable match found for '{col}'. Marking as unknown.")
                    result[col] = {
                        "canonical_name": col,
                        "confidence": 0.0,
                        "reasoning": "No match found",
                        "link": col,
                        "is_unknown": True
                    }
        print("[AIHarmonizer] Fallback harmonization complete.")
        # Also group synonyms for fallback results
        result = self._group_synonyms(result)
        return result

    def _group_synonyms(self, harmonization_result: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Post-processes the harmonization result to group synonyms and update link fields.
        Updates the 'link' field for each column to contain all input columns that map to the same canonical name.
        """
        # First, group by canonical name to find all synonyms
        canonical_groups = {}
        for col, info in harmonization_result.items():
            canonical_name = info["canonical_name"]
            if canonical_name not in canonical_groups:
                canonical_groups[canonical_name] = []
            canonical_groups[canonical_name].append(col)
        
        # Now update each column's link field with all synonyms
        updated_result = {}
        for col, info in harmonization_result.items():
            canonical_name = info["canonical_name"]
            all_synonyms = canonical_groups[canonical_name]
            
            # Update the link field to contain all synonyms (as a string)
            if len(all_synonyms) == 1:
                link_str = all_synonyms[0]
            else:
                link_str = ", ".join(all_synonyms)
            
            updated_result[col] = {
                "canonical_name": canonical_name,
                "confidence": info["confidence"],
                "reasoning": info["reasoning"],
                "link": link_str,
                "is_unknown": info["is_unknown"]
            }
            
        print(f"[AIHarmonizer] Grouped synonyms: {canonical_groups}")
        return updated_result

    def get_mapping_summary(self, harmonization_result: Dict[str, Dict[str, Any]]) -> Dict:
        """
        Generate a summary of the harmonization results.
        """
        print("[AIHarmonizer] Generating mapping summary...")
        total_columns = len(harmonization_result)
        high_confidence = sum(1 for v in harmonization_result.values() if v['confidence'] >= 0.8)
        medium_confidence = sum(1 for v in harmonization_result.values() if 0.5 <= v['confidence'] < 0.8)
        low_confidence = sum(1 for v in harmonization_result.values() if v['confidence'] < 0.5)
        unknown = sum(1 for v in harmonization_result.values() if v['is_unknown'])
        print(f"[AIHarmonizer] Summary: total={total_columns}, high={high_confidence}, medium={medium_confidence}, low={low_confidence}, unknown={unknown}")
        return {
            "total_columns": total_columns,
            "high_confidence": high_confidence,
            "medium_confidence": medium_confidence,
            "low_confidence": low_confidence,
            "unknown": unknown,
            "success_rate": (high_confidence + medium_confidence) / total_columns if total_columns > 0 else 0
        }

def harmonize_columns(input_columns: List[str], context: Optional[str] = None, api_key: Optional[str] = None, sample_data: Optional[Dict[str, List]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Standalone function for column harmonization.
    
    Args:
        input_columns: List of column names to harmonize
        context: Optional context about the data
        api_key: OpenAI API key
        sample_data: Optional sample data for context
        
    Returns:
        Dictionary mapping each input column to harmonization info
    """
    try:
        harmonizer = AIHarmonizer(api_key=api_key)
        return harmonizer.harmonize_columns(input_columns, context=context, sample_data=sample_data)
    except Exception as e:
        print(f"[Harmonizer] Error in harmonize_columns: {e}")
        # Return fallback mappings
        from .fuzzyMatching import fuzzy_match_columns
        fuzzy_mappings = fuzzy_match_columns(input_columns)
        
        result = {}
        for col in input_columns:
            mapped_name = fuzzy_mappings.get(col, col)
            result[col] = {
                'mapped_name': mapped_name,
                'confidence': 0.7 if mapped_name != col else 0.3,
                'method': 'fuzzy_fallback',
                'fallback_used': True,
                'ai_reasoning': f'Fallback mapping: {col} -> {mapped_name}',
                'sample_values': []
            }
        return result 