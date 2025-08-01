#!/usr/bin/env python3
"""
Build and publish script for pdtab package
Usage: python build_and_publish.py [--test]
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'pdtab.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)
    
    print("✅ Cleanup completed")

def check_requirements():
    """Check that required tools are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = ['build', 'twine']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install build twine")
        sys.exit(1)
    
    print("✅ All requirements satisfied")

def run_tests():
    """Run tests before building"""
    print("🧪 Running tests...")
    
    if os.path.exists('test_examples.py'):
        run_command("python test_examples.py", "Running test suite")
    
    if os.path.exists('test_install.py'):
        run_command("python test_install.py", "Running installation tests")

def build_package():
    """Build the package"""
    run_command("python -m build", "Building package")

def check_package():
    """Check the built package"""
    run_command("python -m twine check dist/*", "Checking package")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("📤 Uploading to Test PyPI...")
    print("You will need to enter your Test PyPI credentials.")
    run_command("python -m twine upload --repository testpypi dist/*", "Uploading to Test PyPI")
    print("✅ Package uploaded to Test PyPI")
    print("🔗 Check your package at: https://test.pypi.org/project/pdtab/")

def upload_to_pypi():
    """Upload to PyPI"""
    print("📤 Uploading to PyPI...")
    print("You will need to enter your PyPI credentials.")
    
    response = input("Are you sure you want to upload to PyPI? (y/N): ")
    if response.lower() != 'y':
        print("Upload cancelled.")
        return
    
    run_command("python -m twine upload dist/*", "Uploading to PyPI")
    print("✅ Package uploaded to PyPI")
    print("🔗 Check your package at: https://pypi.org/project/pdtab/")

def main():
    """Main function"""
    test_only = '--test' in sys.argv
    
    print("🚀 pdtab Package Build and Publish Script")
    print("=" * 50)
    
    # Change to package directory
    os.chdir(Path(__file__).parent)
    
    # Check requirements
    check_requirements()
    
    # Clean previous builds
    clean_build()
    
    # Run tests
    run_tests()
    
    # Build package
    build_package()
    
    # Check package
    check_package()
    
    if test_only:
        # Upload to Test PyPI
        upload_to_test_pypi()
        print("\n🎉 Test upload completed!")
        print("To test installation:")
        print("pip install --index-url https://test.pypi.org/simple/ pdtab")
    else:
        # Ask user what to do
        print("\n📋 Built package successfully! What would you like to do?")
        print("1. Upload to Test PyPI (recommended first)")
        print("2. Upload to PyPI")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            upload_to_test_pypi()
        elif choice == '2':
            upload_to_pypi()
        else:
            print("Exiting without upload.")
    
    print("\n🎉 All done!")

if __name__ == '__main__':
    main()
