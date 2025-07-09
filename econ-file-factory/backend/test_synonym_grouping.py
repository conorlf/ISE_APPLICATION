#!/usr/bin/env python3
"""
Test script for the AIHarmonizer synonym grouping functionality.
"""
import sys
sys.path.append('.')

from ai.columnHarmionisation.ai_harmonizer import AIHarmonizer

def test_synonym_grouping():
    """Test the synonym grouping functionality"""
    print("Testing AIHarmonizer synonym grouping...")
    
    # Test columns that should map to synonyms
    test_columns = [
        'company_name', 'firm_name', 'organization',  # Should all map to 'company_name'
        'revenue', 'sales',                           # Should both map to 'revenue' 
        'year', 'yr',                                 # Should both map to 'year'
        'unique_column'                               # Should map to itself
    ]
    
    print(f"Input columns: {test_columns}")
    print()
    
    try:
        # Create harmonizer with fake API key (will use fallback)
        harmonizer = AIHarmonizer(api_key='fake-key-for-testing')
        
        # Test fallback harmonization with synonym grouping
        result = harmonizer._fallback_harmonization(test_columns)
        
        print("Harmonization results:")
        print("-" * 50)
        for col, info in result.items():
            print(f"Input: '{col}'")
            print(f"  -> Canonical: '{info['canonical_name']}'")
            print(f"  -> Link (synonyms): '{info['link']}'")
            print(f"  -> Confidence: {info['confidence']}")
            print()
        
        # Group by canonical name to show the synonym grouping
        print("Grouped by canonical name:")
        print("-" * 50)
        canonical_groups = {}
        for col, info in result.items():
            canonical = info['canonical_name']
            if canonical not in canonical_groups:
                canonical_groups[canonical] = []
            canonical_groups[canonical].append(col)
        
        for canonical, synonyms in canonical_groups.items():
            print(f"'{canonical}': {synonyms}")
            # Check that all synonyms have the same link field
            links = [result[syn]['link'] for syn in synonyms]
            all_same = all(link == links[0] for link in links)
            print(f"  All synonyms have same link field: {all_same}")
            if synonyms:
                print(f"  Link field content: '{result[synonyms[0]]['link']}'")
            print()
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_synonym_grouping() 