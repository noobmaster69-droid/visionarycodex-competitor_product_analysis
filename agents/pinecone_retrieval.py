from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from pinecone import Pinecone, ServerlessSpec
import logging
import json
import ast

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'formal-loop-452705-h1'
REGION = 'us-central1'
PINECONE_API_KEY = 'pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i'
PINECONE_ENV = "us-east1"  # Or "us-west1-gcp" or your env
INDEX_NAME = "product-index"

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    logger.info("Successfully initialized Pinecone")
except Exception as e:
    logger.error("Failed to initialize Pinecone: %s", e)
    raise

try:
    index = pc.Index('product-index')
    logger.info("Successfully connected to Pinecone index")
except Exception as e:
    logger.error("Failed to connect to Pinecone index: %s", e)
    raise

def retrieve_product(product_id: str):
    try:
        fetch_response = index.fetch(ids=[product_id])
        if product_id in fetch_response.vectors:
            retrieved_vector = fetch_response.vectors[product_id]
            return retrieved_vector.metadata
        else:
            return None
    except Exception as e:
        print(f"Error retrieving product: {e}")
        return None


def retrieve_product_by_brand(myBrand: str, listOfProducts: list[str], brand: str):
    try:
        query_results = index.query(
            vector=[0.0] * 768,  # Dummy vector, as it's required but ignored when using a filter
            top_k=10,  # Adjust as needed to retrieve more results
            filter={
                "brand": {"$eq": brand}
            },
            include_metadata=True  # Ensure metadata is included in the results
        )

        if query_results.matches:
            # Return the metadata of the matched vectors
            products = [match.metadata for match in query_results.matches]
            return format_product_details_from_pinecone(myBrand, listOfProducts, products)
        else:
            return None
    except Exception as e:
        print(f"Error retrieving products by brand: {e}")
        return None

def format_product_details_from_pinecone(myBrand, listOfProducts, products):
    size = listOfProducts.__len__()
    for product in products:
        print(product)

        # Step 2: Use ast.literal_eval() to safely convert the string to a Python dictionary
        reviews = ast.literal_eval(product['reviews'])
        details = ast.literal_eval(product['details'])
        features = ast.literal_eval(product['features'])
        insights = ast.literal_eval(product['insights'])

        # reviewSentiment = json.loads(product)
        # details = json.loads(product['details'].replace("'", "\"").replace("True", "true").replace("False", "false"))
        # details['price'] = int(details['price'].replace("'", "\"").replace("True", "true").replace("False", "false")['price'][0].replace('$','').replace(',',''))
        # details['userRating'] = details['userRating']
        # details['numberOfReviews'] = details['numberOfReviews']
        # details['specilFeatures'] = details['specilFeatures']
        # details['reviewSentiment'] = json.loads(details['reviewSentiment'])
        # details['featureImportance'] = json.loads(details['featureImportance'])
        # insights = json.loads(product['insights'].replace("'", "\"").replace("True", "true").replace("False", "false"))
        # features = json.loads(product['features'])
        # review_string = product['reviews']
        # json.loads(review_string)
        # json.load(product['features'])
        if product['brand'] == myBrand:
            isMyCompanyProduct = True
        else:
            isMyCompanyProduct = False

        new_product = {
            'id': size+1,
            'isMyCompanyProduct': isMyCompanyProduct,
            'competitorName': product['brand'],
            'model': product['model'],
            "details": details,
            "insights": insights,
            "reviews": reviews,
            "features": features,
        }
        size = size +1
        listOfProducts.append(new_product)

    return listOfProducts


# Example usage
# product_id_to_retrieve = "Galaxy Z Fold5"
# retrieved_product = retrieve_product(product_id_to_retrieve)
# format_product_details_from_pinecone(retrieve_product_by_brand("Google"))
#
# if retrieved_product:
#     print("Retrieved Product:")
#     print(retrieved_product)
# else:
#     print("Product not found.")