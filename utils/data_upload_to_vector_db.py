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

myProducts = [
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX1 Chip': True, 'FlexOLED Display': True, 'Dual Matrix Camera': True}",
      "insights":
        "{'popularity': 'High', 'priceTrend': 'Rising', 'demand': 'High', 'marketShare': '18%'}",
      "model": "X-Fold Pro",
      "reviews":
        "[{'user': 'TechEarly', 'rating': 4.2, 'comment': 'Innovative folding phone', 'date': '2024-04-15'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX2 Chip': True, '4K HDR Display': True, '100W Fast Charging': True}",
      "insights":
        "{'popularity': 'Very High', 'priceTrend': 'Stable', 'demand': 'Extreme', 'marketShare': '25%'}",
      "model": "Prime 2024",
      "reviews":
        "[{'user': 'PowerUser', 'rating': 4.9, 'comment': 'Best flagship phone', 'date': '2024-03-28'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Lite Chip': True, 'AMOLED Display': True, '48MP Camera': True}",
      "insights":
        "{'popularity': 'Medium', 'priceTrend': 'Decreasing', 'demand': 'Medium', 'marketShare': '12%'}",
      "model": "Nova Lite",
      "reviews":
        "[{'user': 'BudgetBuyer', 'rating': 4.3, 'comment': 'Great mid-range option', 'date': '2024-04-01'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Pro Chip': True, '6.8\" Curved Display': True, '200MP Camera': True}",
      "insights":
        "{'popularity': 'High', 'priceTrend': 'Stable', 'demand': 'High', 'marketShare': '15%'}",
      "model": "Nova Ultra",
      "reviews":
        "[{'user': 'PhotoPro', 'rating': 4.7, 'comment': 'Camera beast!', 'date': '2024-03-22'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Gaming Chip': True, '144Hz Display': True, 'Active Cooling': True}",
      "insights":
        "{'popularity': 'Medium', 'priceTrend': 'Stable', 'demand': 'Medium', 'marketShare': '8%'}",
      "model": "Nova Play",
      "reviews":
        "[{'user': 'MobileGamer', 'rating': 4.5, 'comment': 'Smooth gaming experience', 'date': '2024-04-05'}]",
    },
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
        combined_text = f"Brand: {products['brand']}, Model: {products['model']}, Category: {products['category']}, Features: {products['features']}, Insights: {products['insights']}, Reviews: {products['reviews']}"
        embedding = generate_embeddings(combined_text)
        index.upsert(vectors=[
            (products["model"], embedding, {
                "brand": products["brand"],
                "model": products["model"],
                "category": products["category"],
                "features": str(products["features"]),
                "insights": str(products["insights"]),
                "reviews": str(products["reviews"])
            })
        ])


        logger.info("Successfully uploaded data to Pinecone index")
    except Exception as e:
        logger.error("Failed to upload data to Pinecone index: %s", e)
        raise