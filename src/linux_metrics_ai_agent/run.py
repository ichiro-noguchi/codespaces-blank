import uvicorn
import os
import sys
import importlib.util

# Construct the full path to app.py
app_path = os.path.join("/app", "app.py")

# Load app.py as a module
spec = importlib.util.spec_from_file_location("app_module", app_path)
if spec is None:
    print(f"Error: Could not find app.py at {app_path}", file=sys.stderr)
    sys.exit(1)

app_module = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app_module

try:
    spec.loader.exec_module(app_module)
except FileNotFoundError:
     print(f"Error: Could not find app.py at {app_path}", file=sys.stderr)
     sys.exit(1)
except Exception as e:
    print(f"Error loading app.py: {e}", file=sys.stderr)
    sys.exit(1)


# Get the 'app' object from the loaded module
if not hasattr(app_module, 'app'):
    print("Error: 'app' object not found in app.py", file=sys.stderr)
    sys.exit(1)

app = app_module.app

if __name__ == "__main__":
    # Note: reload=True might not work as expected when loading via importlib
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)
