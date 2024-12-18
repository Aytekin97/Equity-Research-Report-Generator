from pdfminer.high_level import extract_text
import tabula
import camelot

# File path
pdf_file = "TSLA-Q1-2024-Update.pdf"

# Extract text
pdf_text = extract_text(pdf_file)

# Extract tables using tabula (best for simple tables)
tables = tabula.read_pdf(pdf_file, pages="all", multiple_tables=True)

# Alternative: Extract tables using Camelot (best for well-structured PDFs)
try:
    camelot_tables = camelot.read_pdf(pdf_file, pages="1", flavor="stream")
    tables = [table.df for table in camelot_tables]
except Exception as e:
    print("Error extracting tables:", e)

# Print results
print("Extracted Text:", pdf_text[:500])  # Show a preview of the text
print("Extracted Tables:", tables)
