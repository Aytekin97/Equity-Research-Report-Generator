from pdfminer.high_level import extract_text
import pdfplumber
import camelot
import json
import os

# File path
pdf_file_name = "TSLA-Q1-2024-Update.pdf"
text_file_name = "pdf_text.json"
tables_file_name = "pdf_tables.json"



# Extract text
pdf_text = extract_text(pdf_file_name)

# Extract tables using tabula (best for simple tables)
with pdfplumber.open(pdf_file_name) as pdf:
    extracted_text = ""
    tables = []
    for page in pdf.pages:
        extracted_text += page.extract_text() + "\n"
        tables.extend(page.extract_tables())

# Alternative: Extract tables using Camelot (best for well-structured PDFs)
""" try:
    camelot_tables = camelot.read_pdf(pdf_file, pages="1", flavor="stream")
    tables = [table.df for table in camelot_tables]
except Exception as e:
    print("Error extracting tables:", e) """

with open(text_file_name, 'w') as text_file:
    json.dump(extracted_text, text_file, indent=4)

""" with open(tables_file_name, 'w') as tables_file:
    json.dump(tables, tables_file, indent=4) """

# Print results
print("Extracted Text:", extracted_text)  # Show a preview of the text
#print("Extracted Tables:", json.dumps(tables, indent=4))
