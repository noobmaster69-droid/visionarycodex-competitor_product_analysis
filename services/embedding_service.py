from sentence_transformers import SentenceTransformer

# from utils.logger import setup_logger
#
# logger = setup_logger('embedding_service', 'logs/embedding_service.log')


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    def create_embeddings(self, texts):
        """Creates embeddings for a list of texts."""
        # logger.info("Creating embeddings...")
        return self.model.encode(texts).tolist()