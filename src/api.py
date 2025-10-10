"""Flask API for Data Quality Chatbot backend."""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.main import process_chatbot_request
from rag.routes_simple import rag_bp
from accuracy.routes import accuracy_bp
from synthetic.routes import synth_bp
from gold.routes import gold_bp
from metrics.routes import metrics_bp
from checklist.routes import checklist_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(rag_bp)
app.register_blueprint(accuracy_bp)
app.register_blueprint(synth_bp)
app.register_blueprint(gold_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(checklist_bp)


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
