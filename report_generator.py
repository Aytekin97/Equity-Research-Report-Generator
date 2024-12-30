from weasyprint import HTML
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import base64
from typing import List, Union
from schemas import TableSchema, TablesSchema, ReportResponse
from loguru import logger

generated_report_path = os.path.join(os.path.dirname(__file__), "documents\generated_report.json")
class ReportGenerator:

    def __init__(self, client, vector_manager):
        self.client = client
        self.vector_manager = vector_manager


    def prepare_prompt_for_agent(self, analysis: List[dict], tables: TablesSchema):
        """
        Prepare a prompt string for the agent, processing analyses and tables.

        Args:
            analysis (List[dict]): List of analysis dictionaries.
            tables (TablesSchema): A TablesSchema object containing table data.

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
        for table in tables.tables:  # Iterate over tables in the TablesSchema object
            prompt += f"**Table Name:** {table.table_name}\n"
            prompt += f"Columns: {', '.join(table.columns)}\n"
            prompt += "Rows:\n"
            for row in table.rows:
                prompt += f"  - {', '.join(row)}\n"
            prompt += "\n"

        return prompt

    

    def generate_report(self, analysis, tables, agent, schema):
        logger.info("Starting to generate the report")
        logger.info("Prepare prompt for agent")
        data = self.prepare_prompt_for_agent(analysis, tables)
        logger.success("Prompt ready")
        logger.info("Prompting ChatGPT")
        prompt = agent.prompt(data)
        report_template = self.client.query_gpt(prompt, schema)
        logger.success("Response received from ChatGPT")

        """ logger.info("Writing files")
        with open(generated_report_path, 'w') as file:
            json.dump(report_template.dict(), file, indent=4)
        logger.success("Dump success!") """

        return report_template


    def create_pdf_report(self, response: ReportResponse, analysis_generator, output_pdf="report.pdf"):
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
                <p class="document-date">Date: December 25, 2024</p>
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
        for source in analysis_generator.sources:
            if isinstance(source, frozenset):
                # Convert frozenset back to dictionary
                source = dict(source)

            # Extract document_name and date
            document_name = source.get("document_name", "Unknown Document")
            date = source.get("date", "N/A")
            html_content += f"<li>{document_name} - {date}</li>"
        html_content += "</ul>"

        logger.success(f"Success!")
        # Write HTML to PDF
        HTML(string=html_content).write_pdf(output_pdf)

        # Cleanup Graph Images
        for section in response.report_body:
            if section.graph_metadata:
                graph_filename = f"{section.heading.replace(' ', '_')}_graph.png"
                if os.path.exists(graph_filename):
                    os.remove(graph_filename)

        print(f"PDF report generated: {output_pdf}")