"""Flask API for Data Quality Chatbot backend."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.main import process_chatbot_request

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import and register blueprints with error handling
# Critical blueprints are imported first
blueprints_to_register = [
    # Critical features first (simpler, less dependencies)
    ("metrics", "metrics.routes", "metrics_bp"),
    ("checklist", "checklist.routes", "checklist_bp"),
    ("dataset_inspector", "dataset_inspector.routes", "dataset_inspector_bp"),
    ("accuracy", "accuracy.routes", "accuracy_bp"),
    ("gold", "gold.routes", "gold_bp"),
    ("synthetic", "synthetic.routes", "synth_bp"),
    # RAG last (has complex initialization)
    ("rag", "rag.routes_simple", "rag_bp"),
]

for feature_name, module_path, blueprint_name in blueprints_to_register:
    try:
        module = __import__(module_path, fromlist=[blueprint_name])
        blueprint = getattr(module, blueprint_name)
        app.register_blueprint(blueprint)
        print(f"[OK] Registered blueprint: {feature_name}")
    except Exception as e:
        print(f"[FAIL] Failed to register blueprint {feature_name}: {str(e)}")
        # Continue registering other blueprints even if one fails


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify(
        {"status": "Backend is running", "message": "Data Quality Chatbot API"}
    )


@app.route("/ask", methods=["POST"])
def ask_question():
    """Process user answers and generate DSL and PySpark code."""
    try:
        data = request.get_json()
        user_answers = data.get("answers", {})

        print(f"Received answers: {list(user_answers.keys())}")

        # This is a simplified integration. In a real scenario, you'd manage the conversation state.
        # For now, we'll just process the answers and return the generated DSL and PySpark code.

        dsl, pyspark_code, errors, warnings = process_chatbot_request(user_answers)

        print(f"Generated DSL with {len(dsl.get('rules', []))} rules")
        print(f"Generated PySpark code length: {len(pyspark_code)}")
        if warnings:
            print(f"Warnings: {len(warnings)}")
        if errors:
            print(f"Errors: {len(errors)}")

        return jsonify(
            {
                "dsl": dsl,
                "pyspark_code": pyspark_code,
                "errors": errors,
                "warnings": warnings,
            }
        )
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # Catching all exceptions to provide a stable API response
        print(f"Error in ask_question: {ex}")
        return (
            jsonify(
                {"error": str(ex), "dsl": {}, "pyspark_code": "", "errors": [str(ex)]}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
