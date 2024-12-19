import pdfplumber
import json
import os
from loguru import logger

# File path
pdf_file_name = "TSLA-Q1-2024-Update.pdf"
text_file_name = "pdf_text.json"


# Extract text using pdfplumber
def pdf_reader():
    logger.info(f"Starting to read: {pdf_file_name}")
    with pdfplumber.open(pdf_file_name) as pdf:
        extracted_text = ""
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    
    logger.info(f"Text extracted. Length = {len(extracted_text)}")

    with open(text_file_name, 'w') as text_file:
        json.dump(extracted_text, text_file, indent=4)
    
    logger.info(f"Text dumped into file: {text_file_name}")

    return extracted_text
