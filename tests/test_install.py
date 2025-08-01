#!/usr/bin/env python3
"""
Installation test script for pdtab
This script tests the basic functionality without requiring full dependencies
"""

import sys
import os

# Add current directory to path for testing
sys.path.insert(0, os.path.dirname(__file__))

def test_import_structure():
    """Test that the package structure is correct"""
    try:
        # Check if dependencies are available
        dependencies_available = True
        try:
            import pandas
            import numpy
            import scipy
            print("✓ All dependencies (pandas, numpy, scipy) are available")
        except ImportError:
            dependencies_available = False
            print("! Dependencies (pandas, numpy, scipy) not installed - this is expected for structure test")
        
        if dependencies_available:
            # Test full import if dependencies are available
            try:
                import pdtab
                print("✓ Full pdtab import successful")
                
                # Test main functions
                main_functions = ['tabulate', 'tab1', 'tab2', 'tabi']
                available_functions = [f for f in dir(pdtab) if not f.startswith('_')]
                
                for func in main_functions:
                    if func in available_functions:
                        print(f"✓ Function {func} available")
                    else:
                        print(f"✗ Function {func} missing")
                
                return True
                
            except Exception as e:
                print(f"✗ Full import failed: {e}")
                return False
        else:
            # Test structure without importing (just check files exist and are valid Python)
            print("✓ Testing package structure without dependencies...")
            
            python_files = [
                'pdtab/__init__.py',
                'pdtab/core/__init__.py',
                'pdtab/core/oneway.py',
                'pdtab/core/twoway.py', 
                'pdtab/core/summarize.py',
                'pdtab/core/immediate.py',
                'pdtab/stats/__init__.py',
                'pdtab/stats/tests.py',
                'pdtab/utils/__init__.py',
                'pdtab/utils/data_processing.py',
                'pdtab/viz/__init__.py',
                'pdtab/viz/plots.py',
                'pdtab/cli.py'
            ]
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    # Basic syntax check
                    compile(content, py_file, 'exec')
                    print(f"✓ {py_file} syntax OK")
                except SyntaxError as e:
                    print(f"✗ {py_file} syntax error: {e}")
                    return False
                except Exception as e:
                    print(f"✗ {py_file} error: {e}")
                    return False
            
            print("✓ All Python files have valid syntax")
            return True
        
    except Exception as e:
        print(f"✗ Import structure test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'pyproject.toml',  # 改为 pyproject.toml
        'README.md',
        'QUICKSTART.md',
        'LICENSE',
        'MANIFEST.in',
        'pdtab/__init__.py',
        'pdtab/core/__init__.py',
        'pdtab/core/oneway.py',
        'pdtab/core/twoway.py',
        'pdtab/core/summarize.py',
        'pdtab/core/immediate.py',
        'pdtab/stats/__init__.py',
        'pdtab/stats/tests.py',
        'pdtab/utils/__init__.py',
        'pdtab/utils/data_processing.py',
        'pdtab/viz/__init__.py',
        'pdtab/viz/plots.py',
        'pdtab/cli.py',
        'test_examples.py',
        'tutorial.ipynb'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n✗ Missing files: {missing_files}")
        return False
    else:
        print("\n✓ All required files present")
        return True

def test_pyproject_toml():
    """Test that pyproject.toml is valid"""
    try:
        import tomllib
        with open('pyproject.toml', 'rb') as f:
            config = f.read()
            toml_data = tomllib.loads(config.decode('utf-8'))
        
        required_elements = [
            ('project', 'name'),
            ('project', 'version'),
            ('project', 'dependencies'),
            ('build-system', 'requires'),
        ]
        
        for *keys, final_key in required_elements:
            current = toml_data
            for key in keys:
                if key not in current:
                    print(f"✗ pyproject.toml missing section [{key}]")
                    return False
                current = current[key]
            
            if final_key not in current:
                print(f"✗ pyproject.toml missing {'.'.join(keys + [final_key])}")
                return False
            else:
                print(f"✓ pyproject.toml contains {'.'.join(keys + [final_key])}")
        
        # Check specific values
        if toml_data['project']['name'] == 'pdtab':
            print("✓ pyproject.toml has correct package name")
        else:
            print("✗ pyproject.toml has incorrect package name")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ pyproject.toml test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== pdtab Installation Test ===\n")
    
    print("1. Testing file structure...")
    file_test = test_file_structure()
    
    print("\n2. Testing pyproject.toml...")
    config_test = test_pyproject_toml()
    
    print("\n3. Testing import structure...")
    import_test = test_import_structure()
    
    print("\n=== Test Summary ===")
    if all([file_test, config_test, import_test]):
        print("✓ All tests passed! Package structure is correct.")
        print("\nTo install with dependencies:")
        print("  pip install pandas numpy scipy matplotlib seaborn")
        print("  pip install -e .")
        print("\nOr install everything at once:")
        print("  pip install .")
        print("\nTo build and publish:")
        print("  pip install build twine")
        print("  python -m build")
        print("  python -m twine upload dist/*")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
