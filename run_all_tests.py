import subprocess
import sys

test_files = [
    "Any_App_Installation_From_GP_automation.py",
    "Test_features_automation.py",
]

print("\n\n🚀 Starting all tests...\n")

all_passed = True

for test_file in test_files:
    print(f"📋 Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], check=True)
        print(f"✅ {test_file} passed!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ {test_file} failed with exit code: {e.returncode}")
        all_passed = False

if all_passed:
    print("🎉 All tests completed successfully!")
    sys.exit(0)
else:
    print("💥 Some tests failed.")
    sys.exit(1)