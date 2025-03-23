import os
from pinecone import Pinecone, ServerlessSpec, Index
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Set the environment variable for Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\infyvisionarycodex\Downloads\key.json'

# === Config ===

REGION = "us-central1"
PINECONE_API_KEY = "pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i"
PINECONE_ENV = "us-east1" # Or "us-west1-gcp" or your env
INDEX_NAME = "product-index"

GCP_PROJECT_ID = "formal-loop-452705-h1"
BQ_DATASET = "competitor_analysis"
BQ_TABLE = "pinecone_product_vectors"

# === Init Pinecone ===

pc = Pinecone(api_key=PINECONE_API_KEY)

# Ensure the index exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region=PINECONE_ENV
        )
    )

index = pc.Index(INDEX_NAME)

# === Init BigQuery ===

bq_client = bigquery.Client(project=GCP_PROJECT_ID)
dataset_ref = bq_client.dataset(BQ_DATASET)
table_ref = dataset_ref.table(BQ_TABLE)

# === Delete and Create BigQuery Dataset ===

try:
    bq_client.delete_dataset(dataset_ref, delete_contents=True, not_found_ok=True)
    print("✅ BigQuery dataset deleted.")
except Exception as e:
    print(f"❌ Error deleting dataset: {e}")

dataset = bigquery.Dataset(dataset_ref)
dataset.location = REGION
bq_client.create_dataset(dataset)
print("✅ BigQuery dataset created.")

# Verify dataset creation
try:
    bq_client.get_dataset(dataset_ref)
    print("✅ BigQuery dataset verified.")
except NotFound:
    print("❌ BigQuery dataset not found after creation.")

schema = [
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("features", "STRING"),
    bigquery.SchemaField("insights", "STRING"),
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("reviews", "STRING"),
]

table = bigquery.Table(table_ref, schema=schema)
bq_client.create_table(table)
print("✅ BigQuery table created.")

# Verify table creation
try:
    bq_client.get_table(table_ref)
    print("✅ BigQuery table verified.")
except NotFound:
    print("❌ BigQuery table not found after creation.")

def fetch_all_pinecone_vectors(model_ids):
    bq_client = bigquery.Client(project=GCP_PROJECT_ID)
    dataset_ref = bq_client.dataset(BQ_DATASET)
    table_ref = dataset_ref.table(BQ_TABLE)

    # === Delete and Create BigQuery Dataset ===

    try:
        bq_client.delete_dataset(dataset_ref, delete_contents=True, not_found_ok=True)
        print("✅ BigQuery dataset deleted.")
    except Exception as e:
        print(f"❌ Error deleting dataset: {e}")

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = REGION
    bq_client.create_dataset(dataset)
    print("✅ BigQuery dataset created.")

    # Verify dataset creation
    try:
        bq_client.get_dataset(dataset_ref)
        print("✅ BigQuery dataset verified.")
    except NotFound:
        print("❌ BigQuery dataset not found after creation.")

    schema = [
        bigquery.SchemaField("model", "STRING"),
        bigquery.SchemaField("features", "STRING"),
        bigquery.SchemaField("insights", "STRING"),
        bigquery.SchemaField("brand", "STRING"),
        bigquery.SchemaField("reviews", "STRING"),
    ]

    table = bigquery.Table(table_ref, schema=schema)
    bq_client.create_table(table)
    print("✅ BigQuery table created.")

    # Verify table creation
    try:
        bq_client.get_table(table_ref)
        print("✅ BigQuery table verified.")
    except NotFound:
        print("❌ BigQuery table not found after creation.")
    result = index.describe_index_stats()
    total_vector_count = result['total_vector_count']
    print(f"Total vector count: {total_vector_count}")

    # Assuming you have a list of model names to fetch
    # model_ids = ["Pixel 8", "Pixel Fold"]  # Replace with your actual model names
    print(f"Fetching vectors with model IDs: {model_ids}")

    # Fetch the vectors
    vectors = index.fetch(ids=model_ids)
    print(f"Fetched vectors: {vectors}")

    rows = []

    for id, vector in vectors.vectors.items():
        metadata = vector.metadata

        # Ensure the metadata contains the relevant fields
        if all(key in metadata for key in ["brand", "category", "features", "insights", "model", "reviews"]):
            row = {
                "model": metadata.get("model", ""),
                "features": metadata.get("features", ""),
                "insights": metadata.get("insights", ""),
                "brand": metadata.get("brand", ""),
                "reviews": metadata.get("reviews", "")
            }
            rows.append(row)
    print("\n\n\n\n\n\n\n\n")
    logging.info(rows)
    return rows

import time
import logging
from google.api_core.exceptions import NotFound, InternalServerError, ServiceUnavailable

def upload_to_bigquery(input_data, retries=6, delay=2):

    try:
        bq_client.delete_dataset(dataset_ref, delete_contents=True, not_found_ok=True)
        print("✅ BigQuery dataset deleted.")
    except Exception as e:
        print(f"❌ Error deleting dataset: {e}")

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = REGION
    bq_client.create_dataset(dataset)
    print("✅ BigQuery dataset created.")

    # Verify dataset creation
    try:
        bq_client.get_dataset(dataset_ref)
        print("✅ BigQuery dataset verified.")
    except NotFound:
        print("❌ BigQuery dataset not found after creation.")
    rows = fetch_all_pinecone_vectors(input_data)
    for attempt in range(retries):
        try:
            # Ensure the table exists before inserting rows
            bq_client.get_table(table_ref)
            errors = bq_client.insert_rows_json(table_ref, rows)
            if errors:
                logging.error("❌ Errors inserting rows: %s", errors)
            else:
                logging.info("✅ Uploaded %d records to BigQuery.", len(rows))
            return
        except NotFound as e:
            logging.warning("⚠️ Attempt %d: Table not found: %s", attempt + 1, e)
            time.sleep(delay)
        except (InternalServerError, ServiceUnavailable) as e:
            logging.warning("⚠️ Attempt %d: Error inserting rows: %s", attempt + 1, e)
            time.sleep(delay)
        except Exception as e:
            logging.error("❌ Unexpected error: %s", e)
            time.sleep(delay)
    logging.error("❌ Failed to insert rows after %d attempts.", retries)
    raise Exception("Failed to insert rows after multiple attempts")

# pinecone_data = fetch_all_pinecone_vectors()
# upload_to_bigquery(pinecone_data)