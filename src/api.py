from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.main import process_chatbot_request

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    user_answers = data.get("answers", {})

    # This is a simplified integration. In a real scenario, you'd manage the conversation state.
    # For now, we'll just process the answers and return the generated DSL and PySpark code.

    dsl, pyspark_code, errors = process_chatbot_request(user_answers)

    return jsonify({"dsl": dsl, "pyspark_code": pyspark_code, "errors": errors})


if __name__ == "__main__":
    app.run(debug=True)
