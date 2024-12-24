from loguru import logger
from schemas import AnalysisResponseSchema
from agents import (
    profitability_agent, leverage_agent, liquidity_agent, efficiency_agent,
    earnings_quality_agent, growth_agent, valuation_agent, dividend_policy_agent,
    market_sentiment_agent, risk_factors_agent, industry_agent, esg_agent,
    innovation_agent, macroeconomic_agent, diversification_agent, management_agent
)


class Analyzer:

    def generate_analysis(self, client, vector_manager):
        analysis_agents = [
            profitability_agent, leverage_agent, liquidity_agent, efficiency_agent,
            earnings_quality_agent, growth_agent, valuation_agent, dividend_policy_agent,
            market_sentiment_agent, risk_factors_agent
        ]
        extended_analysis_agents = [
            industry_agent, esg_agent, innovation_agent, 
            macroeconomic_agent, diversification_agent, management_agent
        ]

        analysis = []
        corpora = []

        for agent in analysis_agents:

            try: 
                # Getting related chunks
                logger.info("Getting related chunks using vector_manager")
                query_embeddings = vector_manager.vectorize(agent.query)
                related_chunks = vector_manager.retrieve_chunks(query_embeddings)
                logger.success(f"Relative chunks received. Number of chunks: {len(related_chunks)}")
                # Implement somthing that retrieves 5 chunks from each type of data using the query embeddings
                
            except Exception as e:
                logger.error(f"An error occured while generating vectors: {e}")

            try:
                logger.info("Prompting ChatGPT")
                prompt = agent.prompt(corpora)
                response = client.query_gpt(prompt, AnalysisResponseSchema)
                logger.success("Response received from ChatGPT")

                analysis.append(response)
                    
            except Exception as e:
                logger.error(f"An error occured while querying ChatGPT: {e}")