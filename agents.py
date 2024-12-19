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
    role="You are an expert text and table extraction agent specializing in processing raw PDF text into structured formats for financial analysis. Your role is to identify, extract, and structure narrative text and tabular data from financial reports, enabling seamless downstream data analysis.",
    function="Your function is to analyze the provided chunk of text from a financial report extracted using a PDF parsing tool. Separate the text into narrative sections and tabular data. Focus on maintaining the logical structure and clear segmentation of the content. Ensure no information is lost, and that sections are labeled appropriately for future use."
)