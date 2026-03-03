# debug_imports.py
import sys
import os
import traceback

print("=" * 60)
print("PYTHON PATH DEBUGGER")
print("=" * 60)

# Print current directory
print(f"\n📂 Current directory: {os.getcwd()}")

# Print Python path
print("\n🔍 Python path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Check if app module exists
print("\n📁 Checking module structure:")
app_path = os.path.join(os.getcwd(), "app")
if os.path.exists(app_path):
    print(f"  ✅ app directory exists: {app_path}")
    
    # Check models
    models_path = os.path.join(app_path, "models")
    if os.path.exists(models_path):
        print(f"  ✅ models directory exists: {models_path}")
        
        schemas_path = os.path.join(models_path, "schemas.py")
        if os.path.exists(schemas_path):
            print(f"  ✅ schemas.py exists: {schemas_path}")
            print(f"  📏 File size: {os.path.getsize(schemas_path)} bytes")
            
            # Read first few lines
            print("\n📄 First 10 lines of schemas.py:")
            try:
                with open(schemas_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 10:
                            print(f"    {i+1}: {line.rstrip()}")
            except Exception as e:
                print(f"    ❌ Error reading file: {e}")
        else:
            print(f"  ❌ schemas.py NOT FOUND at: {schemas_path}")
    else:
        print(f"  ❌ models directory NOT FOUND at: {models_path}")
else:
    print(f"  ❌ app directory NOT FOUND at: {app_path}")

print("\n" + "=" * 60)
print("ATTEMPTING IMPORTS")
print("=" * 60)

# Try to import step by step
try:
    print("\n1️⃣ Importing app...")
    import app
    print(f"   ✅ app imported from: {app.__file__}")
    
    print("\n2️⃣ Importing app.models...")
    import app.models
    print(f"   ✅ app.models imported from: {app.models.__file__}")
    
    print("\n3️⃣ Importing app.models.schemas...")
    import app.models.schemas as schemas
    print(f"   ✅ schemas imported from: {schemas.__file__}")
    
    print("\n4️⃣ Listing contents of schemas module:")
    for attr in dir(schemas):
        if not attr.startswith('_'):
            print(f"   - {attr}")
    
    print("\n5️⃣ Trying specific imports:")
    from app.models.schemas import MeetingInsights
    print("   ✅ MeetingInsights imported")
    
    from app.models.schemas import TaskItem
    print("   ✅ TaskItem imported")
    
    from app.models.schemas import SemanticAnalysis
    print("   ✅ SemanticAnalysis imported")
    
    from app.models.schemas import SalesCallInsights
    print("   ✅ SalesCallInsights imported")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    print("\n" + "=" * 60)
    print("DETAILED ERROR:")
    traceback.print_exc()
    
    # Check for syntax errors in schemas.py
    print("\n" + "=" * 60)
    print("CHECKING FOR SYNTAX ERRORS IN SCHEMAS.PY")
    try:
        with open(schemas_path, 'r') as f:
            content = f.read()
        compile(content, schemas_path, 'exec')
        print("✅ No syntax errors found in schemas.py")
    except SyntaxError as e:
        print(f"❌ Syntax error in schemas.py at line {e.lineno}: {e}")
        print(f"   Line content: {e.text}")
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")