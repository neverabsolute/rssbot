import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

TARGET_URL = os.environ["WEBHOOK_URL"]


@app.route("/webhook", methods=["POST"])
def webhook_relay():
    # Get the incoming JSON data from the request
    data = request.get_json(force=True, silent=True) or {}

    # Check if 'challenge' key is present
    if "challenge" in data:
        # Mirror the entire request body back as the response
        return jsonify(data), 200
    else:
        # Forward the request data to the target URL
        try:
            forward_response = requests.post(TARGET_URL, json=data)
            forward_response.raise_for_status()

            # Return a simple acknowledgment or the forwarded response if desired
            return (
                jsonify(
                    {
                        "status": "forwarded",
                        "forwarded_response_code": forward_response.status_code,
                        "forwarded_response_text": forward_response.text,
                    }
                ),
                200,
            )
        except requests.RequestException as e:
            # Handle errors if the forward request fails
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
