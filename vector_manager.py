from loguru import logger

class VectorManager():

    def vectorize(self, client, corpus):

        logger.info("Querying to get embeddings")

        # Generate embeddings
        try:
            embedings_response = client.generate_embeddings(corpus)

            # Extract only embeddings from the response
            embedings = [item.embedding for item in embedings_response.data]
            logger.success("Embeddings received and processed")
            return embedings
        
        except Exception as e:
            logger.error(f"An error occured while qurying OpenAI's Embedding Generator")
      