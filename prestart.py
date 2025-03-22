import os
import sys
import platform
import subprocess

# Print basic system info
print("=" * 80)
print("AZURE APP SERVICE DIAGNOSTICS")
print("=" * 80)
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

# Check if app.py exists
if os.path.exists('app.py'):
    print("✅ app.py exists")
    with open('app.py', 'r') as f:
        first_line = f.readline().strip()
        print(f"First line of app.py: {first_line}")
else:
    print("❌ app.py does not exist!")

# Check Python path
print("\nPYTHONPATH:")
for path in sys.path:
    print(f"  - {path}")

# Try importing Flask
try:
    import flask
    print(f"\n✅ Flask is installed (version: {flask.__version__})")
except ImportError as e:
    print(f"\n❌ Flask import error: {e}")

# Try importing app
print("\nTrying to import app directly:")
try:
    sys.path.insert(0, os.getcwd())  # Add current directory to path
    from app import app
    print("✅ Successfully imported app!")
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    print(f"Routes: {routes[:3]}... (total: {len(routes)})")
except Exception as e:
    print(f"❌ Error importing app: {e}")

print("=" * 80)
print("END DIAGNOSTICS")
print("=" * 80) 