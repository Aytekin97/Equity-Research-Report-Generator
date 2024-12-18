import nltk
from loguru import logger

nltk.download('punkt')


# Chunkify the document
def chunkify(text, max_tokens=3000):
    words = nltk.word_tokenize(text)
    chunks = []
    current_chunk = []
    current_chunk_size = 0
    logger.info("Starting to chunkify")

    for word in words:
        current_chunk.append(word)
        current_chunk_size += 1
        if current_chunk_size >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_chunk_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.info(f"Chunkification completed, number of chunks: {len(chunks)}")
    return chunks