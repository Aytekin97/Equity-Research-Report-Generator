from loguru import logger
import os
from flask import Flask, jsonify
from flask_cors import CORS

from agents import chunk_summary_agent, tables_extraction_agent, text_extraction_agent
from openai_client import OpenAiClient
from schemas import ChunkSummaryResponseSchema, PreProcessingResponseSchema, TablesSchema, ExtractedTextSchema
import json
from document_pre_process import pdf_reader

extracted_text_file = "extracted_text.json"
extracted_text_path = os.path.join(os.path.dirname(__file__), extracted_text_file)

extracted_tables_file = "extracted_tables.json"
extracted_tables_path = os.path.join(os.path.dirname(__file__), extracted_text_file)

app = Flask(__name__)
CORS(app)


#@app.route('/api/analyze-reports/<text>', methods=['GET'])
def main():

    client = OpenAiClient()

    extracted_pdf = pdf_reader()

    # Extract tables
    logger.info("Extracting tables")
    try:
        logger.info("Prompting ChatGPT")
        prompt = tables_extraction_agent.prompt(extracted_pdf)
        extracted_tables = client.query_gpt(prompt, TablesSchema)
        logger.info("Response received from ChatGPT")
            
    except Exception as e:
        logger.error(f"An error occured while querying ChatGPT: {e}")

    with open(extracted_tables_path, 'w') as file:
        json.dump(extracted_tables.dict(), file, indent=4)

    logger.info(f"Response dumped into: {extracted_tables_file}")

    # Extract text
    logger.info("Extracting text")
    try:
        logger.info("Prompting ChatGPT")
        prompt = text_extraction_agent.prompt(extracted_pdf)
        extracted_text = client.query_gpt(prompt, ExtractedTextSchema)
        logger.info("Response received from ChatGPT")
            
    except Exception as e:
        logger.error(f"An error occured while querying ChatGPT: {e}")

    with open(extracted_text_path, 'w') as file:
        json.dump(extracted_text.dict(), file, indent=4)

    logger.info(f"Response dumped into: {extracted_text_file}")


    """ with open(path, 'w') as file:
        json.dumps(chunks, file, indent=4) """


    """ summarized_chunks = []
    for chunk in chunks:
        try:
            chunk_summary_agent.set_max_tokens(500)
            prompt = chunk_summary_agent.prompt(chunk)

            chunk_summary = client.query_gpt(prompt, ChunkSummaryResponseSchema)
            summarized_chunks.append(chunk_summary)
            
        except Exception as e:
            logger.error(f"An error occured while getting the chunk summary: {e}") """



""" if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port) """

main()