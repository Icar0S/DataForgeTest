"""Debug import issues in api.py"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

print("=" * 70)
print("DEBUGGING API IMPORTS")
print("=" * 70)

try:
    print("1. Testing individual imports...")

    from flask import Flask

    print("   ✅ Flask imported")

    from flask_cors import CORS

    print("   ✅ Flask-CORS imported")

    from chatbot.main import process_chatbot_request

    print("   ✅ Chatbot imported")

    from rag.routes_simple import rag_bp

    print("   ✅ RAG routes imported")

    from accuracy.routes import accuracy_bp

    print("   ✅ Accuracy routes imported")

    print("\n2. Testing synthetic import...")
    from synthetic.routes import synth_bp

    print("   ✅ Synthetic routes imported")

    print("\n3. Testing Flask app creation...")
    app = Flask(__name__)
    CORS(app)
    print("   ✅ Flask app created")

    print("\n4. Registering blueprints...")
    app.register_blueprint(rag_bp)
    print("   ✅ RAG blueprint registered")

    app.register_blueprint(accuracy_bp)
    print("   ✅ Accuracy blueprint registered")

    app.register_blueprint(synth_bp)
    print("   ✅ Synthetic blueprint registered")

    print("\n5. Checking registered routes...")
    synth_routes = [
        rule for rule in app.url_map.iter_rules() if "/api/synth" in rule.rule
    ]
    print(f"   📊 Synthetic routes found: {len(synth_routes)}")

    if synth_routes:
        for route in synth_routes:
            methods = ",".join(route.methods - {"HEAD", "OPTIONS"})
            print(f"      {methods:10} {route.rule}")

    print("\n✅ All imports and registrations successful!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
