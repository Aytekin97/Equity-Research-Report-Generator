from loguru import logger
import os
from flask import Flask, jsonify
from flask_cors import CORS
from chunkify_data import chunkify

from agents import chunk_summary_agent, pre_processing_agent, tables_extraction_agent
from openai_client import OpenAiClient
from schemas import ChunkSummaryResponseSchema, PreProcessingResponseSchema, TablesSchema
import json
from document_pre_process import pdf_reader

file_name = "pre_processed_response.json"
path = os.path.join(os.path.dirname(__file__), file_name)

app = Flask(__name__)
CORS(app)


#@app.route('/api/analyze-reports/<text>', methods=['GET'])
def main():

    client = OpenAiClient()

    extracted_pdf = pdf_reader()
    #print(text)
    try:
        logger.info("Prompting ChatGPT")
        prompt = tables_extraction_agent.prompt(extracted_pdf)
        pre_prossessed_pdf = client.query_gpt(prompt, TablesSchema)
        logger.info("Response received from ChatGPT")
            
    except Exception as e:
        logger.error(f"An error occured while querying ChatGPT: {e}")

    with open(path, 'w') as file:
        json.dump(pre_prossessed_pdf.dict(), file, indent=4)

    logger.info(f"Response dumped into: {file_name}")
    exit(0)

    #chunks = chunkify(text)

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