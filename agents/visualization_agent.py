import os
import time
import logging
from pinecone import Pinecone, ServerlessSpec, Index
from google.cloud import bigquery
from google.api_core.exceptions import NotFound, InternalServerError, ServiceUnavailable

# Set the environment variable for Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\Users\infyvisionarycodex\Downloads\key.json'

# === Config ===

REGION = "us-central1"
PINECONE_API_KEY = "pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i"
PINECONE_ENV = "us-east1"  # Or "us-west1-gcp" or your env
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

schema = [
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("features", "STRING"),
    bigquery.SchemaField("insights", "STRING"),
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("reviews", "STRING"),
]


def truncate_bigquery_table(bq_client, table_ref):
    """Truncates the BigQuery table by deleting all rows."""
    try:
        table = bq_client.get_table(table_ref)
        query = f"TRUNCATE TABLE `{table_ref.project}.{table_ref.dataset_id}.{table_ref.table_id}`"
        job = bq_client.query(query)
        job.result()  # Wait for the query to complete
        logging.info("✅ BigQuery table truncated.")
        time.sleep(5)  # Wait for 5 seconds
        logging.info("✅ Wait time completed after truncation.")
    except NotFound:
        logging.info("Table %s not found, so not truncated.", table_ref)
    except Exception as e:
        logging.error(f"❌ Error truncating BigQuery table: {e}")
        raise


def fetch_all_pinecone_vectors(model_ids):
    """Fetches vectors from Pinecone based on model IDs."""
    result = index.describe_index_stats()
    total_vector_count = result['total_vector_count']
    print(f"Total vector count: {total_vector_count}")
    print(f"Fetching vectors with model IDs: {model_ids}")

    vectors = index.fetch(ids=model_ids)
    print(f"Fetched vectors: {vectors}")

    rows = []

    for id, vector in vectors.vectors.items():
        metadata = vector.metadata

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

def fetch_and_upload_in_batches(model_ids, batch_size=100):
    """Fetches vectors from Pinecone and uploads them to BigQuery in batches."""
    logging.info("➡️ fetch_and_upload_in_batches function called")  # Confirm function is called
    try:
        bq_client.get_table(table_ref)
        truncate_bigquery_table(bq_client, table_ref)
    except NotFound:
        logging.info("Table %s does not exist, creating it.", table_ref)
        try:
            bq_client.get_dataset(dataset_ref)
        except NotFound:
            logging.info("Dataset %s does not exist, creating it.", dataset_ref)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = REGION
            bq_client.create_dataset(dataset)
            print("✅ BigQuery dataset created.")

        table = bigquery.Table(table_ref, schema=schema)
        bq_client.create_table(table)
        print("✅ BigQuery table created.")
    except Exception as e:
        logging.error(f"❌ Error checking/creating table: {e}")
        raise

    for i in range(0, len(model_ids), batch_size):
        batch_ids = model_ids[i:i + batch_size]
        vectors = index.fetch(ids=batch_ids)
        rows = []

        for id, vector in vectors.vectors.items():
            metadata = vector.metadata
            if all(key in metadata for key in ["brand", "category", "features", "insights", "model", "reviews"]):
                row = {
                    "model": metadata.get("model", ""),
                    "features": metadata.get("features", ""),
                    "insights": metadata.get("insights", ""),
                    "brand": metadata.get("brand", ""),
                    "reviews": metadata.get("reviews", "")
                }
                rows.append(row)
        logging.info("finished fetching data from Pinecone")
        upload_to_bigquery_batch(rows)

def upload_to_bigquery_batch(rows, retries=6, delay=2):
    """Uploads a batch of rows to BigQuery with retries."""
    for attempt in range(retries):
        try:
            errors = bq_client.insert_rows_json(table_ref, rows)
            if errors:
                logging.error("❌ Errors inserting rows: %s", errors)
            else:
                logging.info("✅ Uploaded %d records to BigQuery.", len(rows))
            return
        except (InternalServerError, ServiceUnavailable) as e:
            logging.warning("⚠️ Attempt %d: Error inserting rows: %s", attempt + 1, e)
            time.sleep(delay)
        except Exception as e:
            logging.error("❌ Unexpected error: %s", e)
            time.sleep(delay)
    logging.error("❌ Failed to insert rows after %d attempts.", retries)
    raise Exception("Failed to insert rows after multiple attempts")


def upload_to_bigquery(input_data, retries=6, delay=2):
    """Uploads data to BigQuery with retries."""
    try:
        bq_client.get_table(table_ref)
        truncate_bigquery_table(bq_client, table_ref)
    except NotFound:
        logging.info("Table %s does not exist, creating it.", table_ref)
        table = bigquery.Table(table_ref, schema=schema)
        bq_client.create_table(table)
        logging.info("✅ BigQuery table created.")

    rows = fetch_all_pinecone_vectors(input_data)
    for attempt in range(retries):
        try:
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


# Example usage:
# pinecone_data = fetch_all_pinecone_vectors(["Pixel 8", "Pixel Fold"])
# upload_to_bigquery(["Pixel 8", "Pixel Fold"])
# fetch_and_upload_in_batches(["Galaxy Z Flip5", "Galaxy S24"])
# upload_to_bigquery_batch(data)