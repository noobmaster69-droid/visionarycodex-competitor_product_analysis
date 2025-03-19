from google.cloud import aiplatform

# from utils.logger import setup_logger

# logger = setup_logger('matching_engine_service', 'logs/matching_engine_service.log')


class MatchingEngineService:

    def __init__(self, project_id, location, product_index_name, review_index_name):
        self.project_id = project_id

        self.location = location

        self.product_index_name = product_index_name

        self.review_index_name = review_index_name

        aiplatform.init(project=self.project_id, location=self.location)

    def store_embeddings(self, index_name, ids, embeddings, metadata=None):
        """Stores embeddings in Vertex AI Matching Engine."""

        # logger.info(f"Storing embeddings in Matching Engine: {index_name}")

        index = aiplatform.MatchingEngineIndex(index_name=index_name)

        datapoints = []

        for i, embedding in enumerate(embeddings):
            datapoints.append(aiplatform.MatchingEngineIndex.Datapoint(

                datapoint_id=str(ids[i]),

                feature_vector=embedding,

                restricts=metadata[i] if metadata else None

            ))

        index.upsert_datapoints(datapoints)

    def search_similar_items(self, index_name, query_embedding, top_k=5):
        """Searches for similar items in Vertex AI Matching Engine."""

        # logger.info(f"Searching for similar items in Matching Engine: {index_name}")

        index = aiplatform.MatchingEngineIndex(index_name=index_name)

        results = index.find_neighbors(queries=[query_embedding], neighbor_count=top_k)

        return results[0]