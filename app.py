from loguru import logger
from flask import Flask, jsonify
from flask_cors import CORS
from agents import chunk_summary_agent, tables_extraction_agent, text_extraction_agent
from openai_client import OpenAiClient
from schemas import ChunkSummaryResponseSchema, PreProcessingResponseSchema, TablesSchema, ExtractedTextSchema
from vector_manager import VectorManager
from pdf_manager import PdfManager

import json
import requests
import os


extracted_text_path = os.path.join(os.path.dirname(__file__), "documents\extracted_text.json")
extracted_tables_path = os.path.join(os.path.dirname(__file__), "documents\extracted_tables.json")

text_embeddings_file_name = "text_embeddings.json"
text_embeddings_path = os.path.join(os.path.dirname(__file__), f"documents\{text_embeddings_file_name}")
table_embeddings_file_name = "table_embeddings.json"
table_embeddings_path = os.path.join(os.path.dirname(__file__), f"documents\{table_embeddings_file_name}")


embedings_file_name = "article_embedings.json"
embedings_path = f"documents\{embedings_file_name}"
article_embedings_path = os.path.join(os.path.dirname(__file__), embedings_path)

app = Flask(__name__)
CORS(app)


#@app.route('/api/analyze-reports/<text>', methods=['GET'])
def main():

    client = OpenAiClient()
    vector_manager = VectorManager()
    pdf_manager = PdfManager()

    extracted_pdf = pdf_manager.pdf_reader()

    # Extract tables and text
    extracted_tables = pdf_manager.extract(client, extracted_pdf, TablesSchema, tables_extraction_agent)
    extracted_text = pdf_manager.extract(client, extracted_pdf, ExtractedTextSchema, text_extraction_agent)

    # Format tables for embedding generation

    formatted_tables = pdf_manager.format_table_for_embedding(extracted_tables)

    # Send request to get news articles
    try:       
        news = requests.get("https://fetch-news-to-display-production.up.railway.app/api/news/Tesla").json()
        article_summaries = [item['summary'] for item in news if 'summary' in item]
    except Exception as e:
        logger.error(f"An error occured while sending a request to the DB to receive news articles: {e}")

    # Create embeddings
    text_embeddings = vector_manager.vectorize(client, [extracted_text.text])
    table_embeddings = vector_manager.vectorize(client, formatted_tables)
    article_embeddings = vector_manager.vectorize(client, article_summaries)

    # Dump to JSON file
    with open(article_embedings_path, 'w') as file:
        json.dump(article_embeddings, file, indent=4)

    with open(extracted_tables_path, 'w') as file:
        json.dump(extracted_tables.dict(), file, indent=4)

    with open(extracted_text_path, 'w') as file:
        json.dump(extracted_text.dict(), file, indent=4)

    with open(table_embeddings_path, 'w') as file:
        json.dump(table_embeddings, file, indent=4)

    with open(text_embeddings_path, 'w') as file:
        json.dump(text_embeddings, file, indent=4)


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