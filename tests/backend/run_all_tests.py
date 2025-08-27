#!/usr/bin/env python3
"""
Test runner script to execute all backend tests in sequence.

This script runs all test files and provides a summary of results.
Use this when you want to run the complete test suite.

Prerequisites:
- Backend server running on port 8000
- Valid authentication credentials
- All test dependencies installed
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test(test_name, test_file):
    """Run a single test file and return the result."""
    print(f"\n{'='*60}")
    print(f"Running {test_name}: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Run the test file
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"✅ {test_name} completed successfully")
            print(f"Output:\n{result.stdout}")
            return True, result.stdout
        else:
            print(f"❌ {test_name} failed with return code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            if result.stdout:
                print(f"Standard output:\n{result.stdout}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} timed out after 5 minutes")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {test_name} failed with exception: {e}")
        return False, str(e)

def main():
    """Run all test files and provide a summary."""
    print("Ellipsoid Labs Backend Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing the new areas_of_interest parameter and .env configuration system")
    
    # List of tests to run
    tests = [
        ("Debug Request Test", "debug_request.py"),
        ("Frontend Integration Test", "test_frontend_integration.py"),
        ("Areas of Interest Test", "test_areas_of_interest.py"),
        ("Example Usage Test", "example_usage.py")
    ]
    
    results = []
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_file in tests:
        if os.path.exists(test_file):
            success, output = run_test(test_name, test_file)
            results.append((test_name, success, output))
            if success:
                passed_tests += 1
        else:
            print(f"❌ Test file not found: {test_file}")
            results.append((test_name, False, "File not found"))
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Print individual results
    print(f"\nDetailed Results:")
    for test_name, success, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    # Final status
    if passed_tests == total_tests:
        print(f"\n🎉 All tests passed! The backend is working correctly.")
        print("✅ areas_of_interest parameter is functional")
        print("✅ .env configuration system is working")
        print("✅ Frontend integration is ready")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        print("Common issues:")
        print("  - Backend server not running on port 8000")
        print("  - Authentication credentials incorrect")
        print("  - .env configuration not loaded properly")
        print("  - Azure API keys expired or invalid")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
