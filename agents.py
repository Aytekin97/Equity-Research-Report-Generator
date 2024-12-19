class Agent:
    def __init__(self, name, role, function) -> None:
        self.role: str = role
        self.name: str = name
        self.function: str = function

    def set_max_tokens(self, summary_token_target):
        self.function.format(summary_token_target=summary_token_target)

    def prompt(self, input_prompt):
        system_prompt = f"You are a: {self.name}. Your role is: {self.role}. Your function is: {self.function}. Based on your role and function, do the task you are given. Do not give me anything else other than the given task"

        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": input_prompt}]



chunk_summary_agent = Agent(
    name="Financial Report Summary Agent",
    role="You are an expert financial analysis agent specializing in extracting key insights from financial reports to provide actionable summaries. Your role involves evaluating a company's financial performance, growth trends, risks, and their implications on the stock price.",
    function="Your function is to analyze the provided chunk of text from a financial report and deliver a concise and contextually relevant one-paragraph summary. The summary should focus on the company's financial performance, market trends, growth opportunities, risks, and their potential impact on the stock price. Ensure the summary aligns with the overarching goal of supporting equity analysis, avoiding any unrelated or superficial details. The summary should be maximum {summary_token_target} tokens"
)

pre_processing_agent = Agent(
    name="PDF Pre-Processing Agent",
    role="You are an expert text and table extraction agent specializing in separating raw PDF text into text and tables without performing any analysis.",
    function="""Your function is to extract and separate text from tables in the provided text extracted from a financial report using a PDF parsing tool. 
    
    ### Instructions:
    1. Extract **all text exactly as is, apart from the text belonging to a table**, without any summarization or analysis. 
    2. Extract **all tables**, ensuring the structure is preserved. Include:
      - **Table Name:** A meaningful title if available, otherwise a placeholder like 'Table {number}'.
      - **Columns:** Column headers as they appear in the table.
      - **Rows:** Each row of the table as a list of strings.
      
    Ensure that no information is lost, and that text and tables are clearly separated without any interpretation."""
)

tables_extraction_agent = Agent(
    name="PDF Tables Extraction Agent",
    role="You are an expert in extracting all tables from PDFs while ignoring narrative text.",
    function="""Your function is to extract all tables from the provided PDF content while ignoring all narrative text.
    
    ### Instructions:
    1. Extract **all tables**, ensuring the structure is preserved. Include:
      - **Table Name:** A meaningful title if available, otherwise a placeholder like 'Table {number}'.
      - **Columns:** Column headers as they appear in the table.
      - **Rows:** Each row of the table as a list of strings.

    Ensure that no tabular information is lost, and tables are extracted clearly and accurately."""
)