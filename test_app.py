import os
import sys

print("=== DEPLOYMENT DIAGNOSTICS ===")
print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir("."))

try:
    from app import app
    print("Successfully imported app!")
    print("App routes:", [rule.rule for rule in app.url_map.iter_rules()])
except Exception as e:
    print("Error importing app:", e) 