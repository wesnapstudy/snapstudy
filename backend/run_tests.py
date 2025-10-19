#!/usr/bin/env python3
"""
SnapStudy Backend Test Runner

This script runs all tests in the tests/ directory and provides a summary of results.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_test(test_file):
    """Run a single test file and return the result."""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_file}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        # Run the test
        result = subprocess.run(
            [sys.executable, f"tests/{test_file}"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {test_file} PASSED ({duration:.1f}s)")
            return True, duration
        else:
            print(f"\n❌ {test_file} FAILED ({duration:.1f}s)")
            return False, duration
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {test_file} TIMED OUT (>300s)")
        return False, 300
    except Exception as e:
        print(f"\n💥 {test_file} ERROR: {e}")
        return False, 0


def main():
    """Run all tests and provide summary."""
    print("🚀 SnapStudy Backend Test Suite Runner")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("tests"):
        print("❌ Error: tests/ directory not found. Please run from backend/ directory.")
        sys.exit(1)
    
    # Check AWS credentials
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            identity = result.stdout
            if "hackathon-user-01" in identity:
                print("✅ AWS credentials verified (hackathon-user-01)")
            else:
                print("⚠️  Warning: Not using hackathon-user-01 credentials")
                print("   Some tests may fail due to permissions")
        else:
            print("❌ AWS credentials not configured")
            print("   Please configure AWS credentials before running tests")
    except Exception as e:
        print(f"⚠️  Could not verify AWS credentials: {e}")
    
    # Find all test files
    test_files = []
    tests_dir = Path("tests")
    
    for test_file in tests_dir.glob("test_*.py"):
        test_files.append(test_file.name)
    
    test_files.sort()
    
    if not test_files:
        print("❌ No test files found in tests/ directory")
        sys.exit(1)
    
    print(f"\n📋 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   • {test_file}")
    
    # Ask user which tests to run
    print(f"\n🎯 Test Options:")
    print("   1. Run all tests")
    print("   2. Run specific test")
    print("   3. Run mocked tests only (no AWS required)")
    print("   4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "4":
        print("👋 Exiting...")
        return
    elif choice == "3":
        # Run only mocked tests
        test_files = [f for f in test_files if "mock" in f]
        if not test_files:
            print("❌ No mocked test files found")
            return
    elif choice == "2":
        # Let user select specific test
        print("\n📋 Available tests:")
        for i, test_file in enumerate(test_files, 1):
            print(f"   {i}. {test_file}")
        
        try:
            selection = int(input(f"\nSelect test (1-{len(test_files)}): ")) - 1
            if 0 <= selection < len(test_files):
                test_files = [test_files[selection]]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
    elif choice != "1":
        print("❌ Invalid choice")
        return
    
    # Run selected tests
    print(f"\n🏃 Running {len(test_files)} test(s)...")
    
    results = []
    total_start_time = time.time()
    
    for test_file in test_files:
        passed, duration = run_test(test_file)
        results.append((test_file, passed, duration))
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱️  Total Time: {total_duration:.1f}s")
    
    print(f"\n📋 Detailed Results:")
    for test_file, passed, duration in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_file} ({duration:.1f}s)")
    
    if failed_count == 0:
        print(f"\n🎉 All tests passed! SnapStudy backend is working correctly.")
    else:
        print(f"\n⚠️  {failed_count} test(s) failed. Please check the output above for details.")
    
    print(f"\n💡 Tip: You can run individual tests with:")
    print(f"   python tests/test_name.py")


if __name__ == "__main__":
    main()