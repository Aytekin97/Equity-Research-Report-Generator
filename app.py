from loguru import logger
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agents import equity_report_integration_agent
from openai_client import OpenAiClient
from schemas import ReportResponse
from vector_manager import VectorManager
from analysis_generator import Analyzer
from report_generator import ReportGenerator
from pinecone import Pinecone
from config import settings
import os
import boto3


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production (e.g., ["https://your-frontend.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key,
    aws_secret_access_key=settings.aws_secret_key,
)
bucket_name = settings.bucket_name


@app.post("/api/generate-analysis")
def generate_analysis(company_name: str = Query(...)):
    try:
        # Initialize required components
        company_name = company_name.lower()
        client = OpenAiClient()
        report_generator = ReportGenerator(client, s3_client, bucket_name)
        vector_manager = VectorManager()

        # Access Pinecone indexes
        logger.info("Accessing Pinecone indexes...")
        pc = Pinecone(api_key=settings.pinecone_api_key)
        article_index = pc.Index("article-embeddings")
        text_index = pc.Index("document-text-embeddings")
        table_index = pc.Index("table-embeddings")
        analysis_generator = Analyzer(article_index, text_index, table_index)

        # Generate analysis
        logger.info(f"Generating analyses for company: {company_name}")
        final_analysis = analysis_generator.generate_analysis(client, vector_manager, company_name)
        logger.success("Analyses successfully generated.")
        logger.info(f"Analyses length: {len(final_analysis['analysis'])}")

        # Generate report and create PDF
        report_response = report_generator.generate_report(final_analysis, equity_report_integration_agent, ReportResponse)
        pdf_url = report_generator.create_pdf_report(report_response, final_analysis, company_name, s3_client)

        # Return the PDF URL
        return JSONResponse(
            status_code=200,
            content={"message": "Analysis and report generated successfully.", "pdf_url": pdf_url},
        )

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

