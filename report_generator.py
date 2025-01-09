from weasyprint import HTML
import matplotlib.pyplot as plt
import os
import json
import base64
from typing import List
from schemas import ReportResponse
from loguru import logger
from datetime import datetime


class ReportGenerator:

    def __init__(self, client, s3_client, bucket_name):
        self.client = client
        self.s3_client = s3_client
        self.bucket_name = bucket_name


    def prepare_prompt_for_agent(self, analysis: List[dict], tables: List[tuple]):
        """
        Prepare a prompt string for the agent, processing analyses and tables.

        Args:
            analysis (List[dict]): List of analysis dictionaries.
            tables (List[tuple]): A list of tuples representing table data.
                Each tuple is expected to have the structure:
                (table_name, table_columns, table_rows)

        Returns:
            str: A formatted string prompt for the agent.
        """
        prompt = "Equity Research Report Data\n\n"

        # Add analyses
        prompt += "### Analyses ###\n"
        for idx, item in enumerate(analysis, start=1):
            prompt += f"{idx}. **Agent:** {item['Agent']}\n"
            prompt += f"   **Analysis:** {item['Analysis']}\n\n"

        # Add tables
        prompt += "### Tables ###\n"
        for table_entry in tables:  # Iterate over the list of table tuples
            table_name, table_columns, table_rows = table_entry  # Unpack tuple

            prompt += f"**Table Name:** {table_name}\n"
            prompt += f"Columns: {', '.join(table_columns)}\n"
            prompt += "Rows:\n"
            
            # If table_rows is a JSON string, convert it to a Python list
            if isinstance(table_rows, str):
                try:
                    table_rows = json.loads(table_rows)  # Parse JSON string into a list
                except json.JSONDecodeError:
                    prompt += "  - [Error parsing rows]\n"
                    continue

            # Add rows to the prompt
            for row in table_rows:
                prompt += f"  - {', '.join(row)}\n"
            prompt += "\n"

        return prompt


    def generate_report(self, analysis, agent, schema):
        logger.info("Starting to generate the report")
        logger.info("Prepare prompt for agent")
        data = self.prepare_prompt_for_agent(analysis['analysis'], analysis['tables'])
        logger.success("Prompt ready")
        logger.info("Prompting ChatGPT")
        prompt = agent.prompt(data)
        report_template = self.client.query_gpt(prompt, schema)
        logger.success("Response received from ChatGPT")

        return report_template


    def create_pdf_report(self, response: ReportResponse, final_analysis, company_name):
        document_date = datetime.now().strftime("%B %d, %Y")
        logger.info("Starting to generate the PDF file")
        logo_path = os.path.abspath("documents/Logo Final.jpg")
        with open(logo_path, "rb") as image_file:
            base64_logo_string = base64.b64encode(image_file.read()).decode()
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                h1, h2 {{ color: #2E3A87; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f4f4f4; }}
                img {{ max-width: 100%; margin: 20px 0; }}
                @page {{
                    margin: 1in;
                }}

                header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    margin-top: -70px;
                }}

                .logo {{
                    width: 100px;
                }}

                .document-info {{
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                }}

                .document-title {{
                    font-size: 20px;
                    font-weight: bold;
                    margin: 0;
                }}

                .document-date {{
                    font-size: 14px;
                    margin: 0;
                    color: gray;
                }}

                hr {{
                    border: none;
                    border-top: 2px solid #000;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
        <header>
            <img src="data:image/png;base64,{base64_logo_string}" alt="Company Logo" class="logo">
            <div class="document-info">
                <p class="document-title">Equity Research Report</p>
                <p class="document-date">{document_date}</p>
            </div>
        </header>
        <hr>
        """
        logger.info(f"Mapping the body")
        for section in response.report_body:
            # Add Heading
            html_content += f"<h1>{section.heading}</h1>"
            
            # Add Content
            html_content += f"<p>{section.content}</p>"
            
            # Add Table if Available
            if section.table_data:
                html_content += f"<h2>{section.table_caption or 'Table'}</h2>"
                columns = section.table_data.columns
                rows = section.table_data.rows
                html_content += "<table><tr>"
                for col in columns:
                    html_content += f"<th>{col}</th>"
                html_content += "</tr>"
                for row in rows:
                    html_content += "<tr>"
                    for cell in row:
                        html_content += f"<td>{cell}</td>"
                    html_content += "</tr>"
                html_content += "</table>"
            
            # Add Graph if Available
            if section.graph_metadata:
                graph_meta = section.graph_metadata
                x_axis = graph_meta.x_axis
                y_data = graph_meta.y_data
                graph_type = graph_meta.type
                
                # Create Graph
                plt.figure(figsize=(8, 5))
                for label, data in y_data.items():
                    if graph_type == "line":
                        plt.plot(x_axis, data, label=label)
                    elif graph_type == "bar":
                        plt.bar(x_axis, data, label=label)
                plt.title(section.figure_caption or "Graph")
                plt.xlabel("Quarter")
                plt.ylabel("Values")
                plt.legend()
                plt.grid()
                
                # Save Graph
                graph_filename = f"{section.heading.replace(' ', '_')}_graph.png"
                graph_path = os.path.abspath(graph_filename)
                print(graph_path)
                plt.savefig(graph_filename)
                plt.close()
                with open(graph_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read()).decode()

                # Add Graph to HTML
                html_content += f"<h2>{section.figure_caption or 'Graph'}</h2>"
                html_content += f'<img src="data:image/png;base64,{base64_string}" alt="{section.heading} Graph">'
        logger.info(f"Mapping references")
        # Add References Section
        html_content += "<h1>References</h1><ul>"
        for source in final_analysis['sources']:

            # Extract document_name and date
            document_name = source[0]
            date = source[1]
            html_content += f"<li>{document_name} - {date}</li>"
        html_content += "</ul>"

        logger.success(f"Success!")
        # Write HTML to PDF
        output_pdf = f"{company_name} Equity Research Report - {document_date}"
        HTML(string=html_content).write_pdf(output_pdf)

        # Upload PDF to S3
        logger.info(f"Uploading {output_pdf} to S3")
        pdf_key = f"reports/{os.path.basename(output_pdf)}"
        with open(output_pdf, "rb") as pdf_file:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=pdf_key,
                Body=pdf_file,
                ContentType="application/pdf"
            )

        pdf_url = f"https://{self.bucket_name}.s3.amazonaws.com/{pdf_key}"
        logger.success(f"PDF uploaded to S3: {pdf_url}")

        # Cleanup local PDF file
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
            logger.info(f"Local PDF file {output_pdf} removed.")

        # Cleanup Graph Images
        for section in response.report_body:
            if section.graph_metadata:
                graph_filename = f"{section.heading.replace(' ', '_')}_graph.png"
                if os.path.exists(graph_filename):
                    os.remove(graph_filename)

        print(f"PDF report generated: {pdf_url}")
        return pdf_url