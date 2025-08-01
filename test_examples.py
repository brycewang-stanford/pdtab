"""
Test Examples for pdtab
======================

This file contains example usage and tests for the pdtab library.
Run this to verify the library works correctly.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the pdtab directory to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import pdtab
    print("✓ pdtab imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pdtab: {e}")
    sys.exit(1)


def create_test_data():
    """Create test dataset similar to examples in documentation."""
    np.random.seed(42)
    
    n = 100
    data = {
        'gender': np.random.choice(['Male', 'Female'], n, p=[0.6, 0.4]),
        'education': np.random.choice(['High School', 'College', 'Graduate'], n, p=[0.4, 0.4, 0.2]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'income': np.random.normal(50000, 15000, n),
        'age': np.random.normal(35, 10, n),
        'satisfaction': np.random.choice([1, 2, 3, 4, 5], n)
    }
    
    # Add some missing values
    missing_indices = np.random.choice(n, 5, replace=False)
    for idx in missing_indices:
        data['education'][idx] = None
    
    df = pd.DataFrame(data)
    return df


def test_oneway_tabulation():
    """Test one-way tabulation functionality."""
    print("\n" + "="*50)
    print("Testing One-way Tabulation")
    print("="*50)
    
    df = create_test_data()
    
    try:
        # Basic one-way table
        result = pdtab.tabulate('gender', data=df)
        print("Basic one-way tabulation:")
        print(result)
        print("✓ One-way tabulation successful")
        
        # With sorting
        result = pdtab.tabulate('education', data=df, sort=True)
        print("\nSorted by frequency:")
        print(result)
        print("✓ Sorted tabulation successful")
        
        # With missing values included
        result = pdtab.tabulate('education', data=df, missing=True)
        print("\nWith missing values:")
        print(result)
        print("✓ Missing value handling successful")
        
    except Exception as e:
        print(f"✗ One-way tabulation failed: {e}")
        return False
    
    return True


def test_twoway_tabulation():
    """Test two-way tabulation functionality."""
    print("\n" + "="*50)
    print("Testing Two-way Tabulation")
    print("="*50)
    
    df = create_test_data()
    
    try:
        # Basic two-way table
        result = pdtab.tabulate('gender', 'education', data=df)
        print("Basic two-way tabulation:")
        print(result)
        print("✓ Two-way tabulation successful")
        
        # With statistical tests
        result = pdtab.tabulate('gender', 'education', data=df, chi2=True, V=True)
        print("\nWith statistical tests:")
        print(result)
        if result.statistics:
            print(f"Chi-square statistic: {result.statistics.get('chi2', {}).get('statistic', 'N/A')}")
            print(f"Cramér's V: {result.statistics.get('cramers_v', 'N/A')}")
        print("✓ Statistical tests successful")
        
        # With percentages
        result = pdtab.tabulate('gender', 'education', data=df, row=True, column=True)
        print("\nWith row and column percentages:")
        print(result)
        print("✓ Percentage calculations successful")
        
    except Exception as e:
        print(f"✗ Two-way tabulation failed: {e}")
        return False
    
    return True


def test_summary_tabulation():
    """Test summary tabulation functionality."""
    print("\n" + "="*50)
    print("Testing Summary Tabulation")
    print("="*50)
    
    df = create_test_data()
    
    try:
        # One-way summary
        result = pdtab.tabulate('gender', data=df, summarize='income')
        print("Summary tabulation (income by gender):")
        print(result)
        print("✓ One-way summary successful")
        
        # Two-way summary
        result = pdtab.tabulate('gender', 'education', data=df, summarize='age')
        print("\nTwo-way summary (age by gender and education):")
        print(result)
        print("✓ Two-way summary successful")
        
    except Exception as e:
        print(f"✗ Summary tabulation failed: {e}")
        return False
    
    return True


def test_immediate_tabulation():
    """Test immediate tabulation functionality."""
    print("\n" + "="*50)
    print("Testing Immediate Tabulation")
    print("="*50)
    
    try:
        # String format
        result = pdtab.tabi("30 18 \\ 38 14", exact=True)
        print("Immediate tabulation from string:")
        print(result)
        if result.statistics:
            print(f"Fisher's exact p-value: {result.statistics.get('exact', {}).get('p_value', 'N/A')}")
        print("✓ String format successful")
        
        # List format
        table_data = [[25, 35, 40], [15, 20, 30]]
        result = pdtab.tabi(table_data, chi2=True)
        print("\nImmediate tabulation from list:")
        print(result)
        print("✓ List format successful")
        
    except Exception as e:
        print(f"✗ Immediate tabulation failed: {e}")
        return False
    
    return True


def test_multiple_tables():
    """Test tab1 and tab2 functions."""
    print("\n" + "="*50)
    print("Testing Multiple Table Functions")
    print("="*50)
    
    df = create_test_data()
    
    try:
        # tab1 - multiple one-way tables
        results = pdtab.tab1(['gender', 'education'], data=df)
        print("Multiple one-way tables (tab1):")
        for var, result in results.items():
            print(f"\n{var}:")
            print(result)
        print("✓ tab1 successful")
        
        # tab2 - all two-way combinations
        results = pdtab.tab2(['gender', 'education', 'region'], data=df)
        print(f"\nAll two-way tables (tab2) - {len(results)} combinations:")
        for (var1, var2), result in list(results.items())[:2]:  # Show first 2
            print(f"\n{var1} × {var2}:")
            print(result)
        print("✓ tab2 successful")
        
    except Exception as e:
        print(f"✗ Multiple table functions failed: {e}")
        return False
    
    return True


def test_weights():
    """Test weighted tabulation."""
    print("\n" + "="*50)
    print("Testing Weighted Tabulation")
    print("="*50)
    
    df = create_test_data()
    
    try:
        # Add weight column
        df['weights'] = np.random.uniform(0.5, 2.0, len(df))
        
        # Weighted tabulation
        result = pdtab.tabulate('gender', data=df, weights='weights')
        print("Weighted one-way tabulation:")
        print(result)
        print("✓ Weighted tabulation successful")
        
    except Exception as e:
        print(f"✗ Weighted tabulation failed: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("PDTAB Library Test Suite")
    print("="*50)
    
    tests = [
        test_oneway_tabulation,
        test_twoway_tabulation,
        test_summary_tabulation,
        test_immediate_tabulation,
        test_multiple_tables,
        test_weights
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("="*50)
    
    if passed == total:
        print("🎉 All tests passed! pdtab is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
