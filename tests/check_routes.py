"""Test script to check registered Flask routes."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    from api import app

    print("=" * 70)
    print("REGISTERED FLASK ROUTES")
    print("=" * 70)

    for rule in app.url_map.iter_rules():
        methods = ",".join(rule.methods - {"HEAD", "OPTIONS"})
        print(f"{methods:10} {rule.rule}")

    print(f"\n📊 Total routes: {len(list(app.url_map.iter_rules()))}")

    # Check if synthetic routes are there
    synth_routes = [
        rule for rule in app.url_map.iter_rules() if "/api/synth" in rule.rule
    ]
    print(f"🧪 Synthetic routes: {len(synth_routes)}")

    if synth_routes:
        print("✅ Synthetic module routes found:")
        for route in synth_routes:
            methods = ",".join(route.methods - {"HEAD", "OPTIONS"})
            print(f"   {methods:10} {route.rule}")
    else:
        print("❌ No synthetic routes found!")

except Exception as e:
    print(f"❌ Error checking routes: {e}")
    import traceback

    traceback.print_exc()
