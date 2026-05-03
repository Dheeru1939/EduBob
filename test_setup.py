"""
Test script to verify EduBob v2 setup
Run this before starting the app to check dependencies and configuration
"""

import sys
import os

def test_imports():
    """Test that all required packages are installed"""
    print("Testing package imports...")
    
    try:
        import streamlit
        print("✓ streamlit installed")
    except ImportError:
        print("✗ streamlit NOT installed - run: pip install streamlit>=1.30")
        return False
    
    try:
        import ibm_watsonx_ai
        print("✓ ibm-watsonx-ai installed")
    except ImportError:
        print("✗ ibm-watsonx-ai NOT installed - run: pip install ibm-watsonx-ai>=1.0")
        return False
    
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv NOT installed - run: pip install python-dotenv>=1.0")
        return False
    
    return True


def test_env_file():
    """Test that .env file exists and has required variables"""
    print("\nTesting environment configuration...")
    
    if not os.path.exists(".env"):
        print("✗ .env file NOT found")
        print("  Create .env file from .env.example and fill in your credentials")
        return False
    
    print("✓ .env file exists")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["WATSONX_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_URL"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "your_key_here" or value == "your_project_id_here":
            missing.append(var)
        else:
            print(f"✓ {var} is set")
    
    if missing:
        print(f"✗ Missing or placeholder values for: {', '.join(missing)}")
        print("  Update your .env file with actual credentials")
        return False
    
    return True


def test_watsonx_connection():
    """Test connection to watsonx.ai"""
    print("\nTesting watsonx.ai connection...")
    
    try:
        from core.watsonx_client import test_connection
        success = test_connection()
        
        if success:
            print("✓ Watsonx.ai connection successful!")
            return True
        else:
            print("✗ Watsonx.ai connection failed")
            print("  Check your credentials and network connection")
            return False
    except Exception as e:
        print(f"✗ Error testing connection: {e}")
        return False


def test_core_modules():
    """Test that core modules can be imported"""
    print("\nTesting core modules...")
    
    modules = [
        "core.watsonx_client",
        "core.prompts",
        "core.code_runner",
        "core.state",
        "core.adaptation"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imports successfully")
        except Exception as e:
            print(f"✗ {module} import failed: {e}")
            return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("EduBob v2 Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Package imports", test_imports()))
    results.append(("Environment config", test_env_file()))
    results.append(("Core modules", test_core_modules()))
    
    # Only test connection if previous tests passed
    if all(r[1] for r in results):
        results.append(("Watsonx.ai connection", test_watsonx_connection()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Ready to run EduBob v2")
        print("\nStart the app with:")
        print("  streamlit run app.py")
    else:
        print("✗ Some tests failed. Fix the issues above before running.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
