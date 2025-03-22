from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from pinecone import Pinecone, ServerlessSpec
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'formal-loop-452705-h1'
REGION = 'us-central1'
PINECONE_API_KEY = 'pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i'
PINECONE_ENV = "us-east1"  # Or "us-west1-gcp" or your env
INDEX_NAME = "product-index"

# Sample data for recipes
products = [
    {"brand": "Samsung", "model": "Galaxy S24+", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Dynamic AMOLED 2X": True, "Enhanced Telephoto Lens": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "18%"}, "reviews": [{"user": "TechEnthusiast", "rating": 4.6, "comment": "Great all-around phone", "date": "2024-03-05"}]}
]

# Function to generate embeddings for dietary preferences
def generate_embeddings(text):
    aiplatform.init(project=PROJECT_ID, location=REGION)
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
    return embedding_model.get_embeddings([text])[0].values


def upsert_data(products):
    # Initialize Pinecone
    try:
        pc = Pinecone(api_key='pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i')
        logger.info("Successfully initialized Pinecone")
    except Exception as e:
        logger.error("Failed to initialize Pinecone: %s", e)
        raise

    # Create a Pinecone index with the correct dimension
    index_name = 'product-index'
    dimension = 1024

    # Connect to the index
    try:
        index = pc.Index(index_name)
        logger.info("Successfully connected to Pinecone index")
    except Exception as e:
        logger.error("Failed to connect to Pinecone index: %s", e)
        raise

    # Store recipe data in the index
    try:
        for product in products:
            combined_text = f"Brand: {product['brand']}, Model: {product['model']}, Category: {product['category']}, Features: {product['features']}, Insights: {product['insights']}, Reviews: {product['reviews']}"
            embedding = generate_embeddings(combined_text)
            index.upsert(vectors=[
                (product["model"], embedding, {
                    "brand": product["brand"],
                    "model": product["model"],
                    "category": product["category"],
                    "features": str(product["features"]),
                    "insights": str(product["insights"]),
                    "reviews": str(product["reviews"])
                })
            ])
        logger.info("Successfully uploaded data to Pinecone index")
    except Exception as e:
        logger.error("Failed to upload data to Pinecone index: %s", e)
        raise