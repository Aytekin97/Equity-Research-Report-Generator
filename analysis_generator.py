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
        
        for agent in analysis_agents:

            corpora = []
            try:
                # Generate embeddings for the agent query
                logger.info(f"Generating embeddings for agent: {agent.name}")
                query_embeddings = vector_manager.vectorize(client, agent.query)

                # Retrieve chunks for all data types
                logger.info("Retrieving relevant chunks for the query")
                related_chunks = vector_manager.retrieve_chunks(query_embeddings)

                logger.success(f"Related chunks received. Total: {len(related_chunks)}")
                # Extract relevant text from chunks based on key availability
                corpora.extend(
                    chunk["chunk"] if "chunk" in chunk else
                    chunk["table"] if "table" in chunk else
                    chunk["article"] for chunk in related_chunks
                )

            except Exception as e:
                logger.error(f"An error occurred while generating vectors or retrieving chunks: {e}")


            try:
                # Prompting ChatGPT with corpora
                logger.info("Prompting ChatGPT")
                
                # Convert corpora (list of chunks) to a single string
                formatted_corpora = "\n\n".join(corpora)  # Separate chunks with double newlines for readability

                # Create the prompt using the agent's method
                prompt = agent.prompt(formatted_corpora)

                # Query ChatGPT with the constructed prompt
                response = client.query_gpt(prompt, AnalysisResponseSchema)
                logger.success("Response received from ChatGPT")

                # Append the response to the analysis
                analysis.append({"Agent": agent.name, "Analysis": response.analysis})

            except Exception as e:
                logger.error(f"An error occurred while querying ChatGPT: {e}")

        return analysis
