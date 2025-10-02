import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.main import process_chatbot_request

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/", methods=["GET"])
def health_check():
    return jsonify(
        {"status": "Backend is running", "message": "Data Quality Chatbot API"}
    )


@app.route("/ask", methods=["POST"])
def ask_question():
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
    except Exception as ex:
        print(f"Error in ask_question: {ex}")
        return (
            jsonify(
                {"error": str(ex), "dsl": {}, "pyspark_code": "", "errors": [str(ex)]}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
