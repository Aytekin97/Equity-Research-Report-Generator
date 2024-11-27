from loguru import logger
import os
from flask import Flask, jsonify
from flask_cors import CORS

from agents import chunk_summary_agent
from openai_client import OpenAiClient

app = Flask(__name__)
CORS(app)


@app.route('/api/analyze-reports/<chunk>', methods=['GET'])
def main(chunk):
    client = OpenAiClient()
    chunk_summary_agent(chunk, client)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
