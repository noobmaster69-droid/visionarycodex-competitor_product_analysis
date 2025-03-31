import os
import time
import logging
import psycopg2
import json
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
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("features", "RECORD", fields=[
        bigquery.SchemaField("chip", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("display", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("battery", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("waterResistance", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("wirelessCharging", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("security", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bluetooth", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("wifi", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("gps", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("nfc", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("dualSim", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("assistant", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("weight", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("protection", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("thumbnail", "STRING", mode="NULLABLE")
    ]),
    bigquery.SchemaField("insights", "RECORD", fields=[
        bigquery.SchemaField("popularity", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("priceTrend", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("demand", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("Availability", "STRING", mode="NULLABLE")
    ]),
    bigquery.SchemaField("details", "RECORD", fields=[
        bigquery.SchemaField("price", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("userRating", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("numberOfReviews", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("specialFeatures", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("reviewSentiment", "RECORD", fields=[
            bigquery.SchemaField("positive", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("negative", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("neutral", "STRING", mode="NULLABLE")
        ], mode="NULLABLE"),
        bigquery.SchemaField("featureImportance", "RECORD", fields=[
            bigquery.SchemaField("price", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("userRating", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("specialFeatures", "FLOAT", mode="NULLABLE")
        ], mode="NULLABLE")
    ]),
]

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

        if all(key in metadata for key in ["brand", "details", "features", "insights", "model", "reviews"]):
            if 'details' in metadata:
                details = json.loads(metadata.get('details', '{}').replace("'", "\"").replace("True", "true").replace("False", "false"))
            else:
                details = ""
            if 'features' in metadata:
                features = json.loads(metadata.get('features', '{}').replace("'", "\"").replace("True", "true").replace("False", "false"))
            else:
                features = ""
            if 'insights' in metadata:
                insights = json.loads(metadata.get('insights', '{}').replace("'", "\"").replace("True", "true").replace("False", "false"))
            else:
                insights = ""
            row = {
                "model": metadata.get("model", ""),
                "details": details,
                "features": features,
                "insights": insights,
                "brand": metadata.get("brand", ""),
            }
            rows.append(row)
    logging.info(rows)
    return rows

def format_string_for_json_loads(input_string):
    """
    Formats a string to be compatible with json.loads().

    This function replaces single quotes with double quotes and ensures
    boolean values are represented in lowercase (true/false). It also escapes
    unescaped double quotes within the string.

    Args:
        input_string (str): The string to format.

    Returns:
        str: The formatted string.
    """
    # Replace single quotes with double quotes
    formatted_string = input_string.replace("'", "\"")

    # Escape unescaped double quotes
    formatted_string = "".join([f"\\{char}" if char == "\"" and i > 0 and formatted_string[i-1] != "\\" else char for i, char in enumerate(formatted_string)])

    # Ensure boolean values are lowercase
    formatted_string = formatted_string.replace("'", "\"").replace("True", "true").replace("False", "false")

    return formatted_string


def fetch_and_upload_in_batches(model_ids, batch_size=100):
    """Fetches vectors from Pinecone and uploads them to BigQuery in batches."""
    logging.info("➡️ fetch_and_upload_in_batches function called")  # Confirm function is called
    try:
        bq_client.get_table(table_ref)
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

    for model_id in model_ids:  # Iterate through each model_id
        # First, perform the query to get the IDs of the matching vectors
        query_results = index.query(
            vector=[0.0] * 768,  # Dummy vector, as it's required but ignored when using a filter
            top_k=10,  # Adjust as needed to retrieve more results
            filter={
                "brand": {"$eq": model_id}  # Use the current model_id
            },
            include_metadata=True  # Ensure metadata is included in the results
        )

        # Extract the IDs of the matching vectors from the query results
        vector_ids = [match.id for match in query_results.matches]

        # Then, fetch the vectors using their IDs
        vectors = index.fetch(ids=vector_ids)
        # vectors = index.fetch(ids=batch_ids)
        rows = []

        for id, vector in vectors.vectors.items():
            metadata = vector.metadata
            if all(key in metadata for key in ["brand", "details", "features", "insights", "model", "reviews"]):
                row = {
                    "model": metadata.get("model", ""),
                    "brand": metadata.get("brand", ""),
                    "features": json.loads(
                        metadata.get("features", '{}').replace("'", "\"").replace("True", "true").replace("False",
                                                                                                          "false")),
                    "insights": json.loads(
                        metadata.get("insights", '{}').replace("'", "\"").replace("True", "true").replace("False",
                                                                                                          "false")),
                    "details": details if (details := json.loads(
                        metadata.get("details", '{}').replace("'", "\"").replace("True", "true").replace("False",
                                                                                                          "false"))) else None
                }

                if details:
                    row["details"] = {
                        "price": details.get("price")[0] if isinstance(details, dict) and details else None,
                        "userRating": details.get("userRating") if isinstance(details, dict) else None,
                        "numberOfReviews": details.get("numberOfReviews") if isinstance(details, dict) else None,
                        "specialFeatures": ', '.join(details.get("specialFeatures")) if isinstance(details,
                                                                                                   dict) and details.get(
                            "specialFeatures") else None,
                        "reviewSentiment": details.get("reviewSentiment") if isinstance(details, dict) else None,
                        "featureImportance": details.get("featureImportance") if isinstance(details, dict) else None
                    }
                else:
                    row["details"] = None

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

# fetch_and_upload_in_batches(["Samsung", "Apple", "Google"])

# result = fetch_all_pinecone_vectors(["Pixel 7 128GB 5G Smartphone", "C11 2021", "Zenfone 11 Ultra", "ROG Phone 9 Pro Unlocked Android Phone"])
#
#
# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#
# class PostgresDB:
#     def __init__(self, dbname, user, password, host, port):
#         """
#         Initializes the PostgresDB class with database connection parameters.
#         """
#         self.dbname = 'product-search-data'
#         self.user = 'postgres'
#         self.password = 'root'
#         self.host = '35.184.42.158'
#         self.port = 5432
#         self.conn = None
#
#     def connect(self):
#         """
#         Establishes a connection to the PostgreSQL database.
#         """
#         try:
#             self.conn = psycopg2.connect(
#                 dbname=self.dbname,
#                 user=self.user,
#                 password=self.password,
#                 host=self.host,
#                 port=self.port
#             )
#             logging.info("Successfully connected to the database.")
#         except psycopg2.Error as e:
#             logging.error(f"Connection error: {e}")
#             raise
#
#     def close(self):
#         """
#         Closes the connection to the PostgreSQL database.
#         """
#         if self.conn:
#             self.conn.close()
#             logging.info("Database connection closed.")
#
#     def execute_query(self, query, params=None):
#         """
#         Executes a SQL query.
#
#         Parameters:
#         - query (str): The SQL query to execute.
#         - params (tuple, optional): Parameters to pass to the query. Defaults to None.
#
#         Returns:
#         - list: A list of tuples containing the results of the query, or None if the query does not return results.
#         """
#         try:
#             with self.conn.cursor() as cur:
#                 cur.execute(query, params)
#                 if cur.description:
#                     return cur.fetchall()
#                 else:
#                     self.conn.commit()
#                     return None
#         except psycopg2.Error as e:
#             self.conn.rollback()
#             logging.error(f"Execution error: {e}")
#             raise
#
#     def truncate_table(self, table_name):
#         """
#         Truncates a specified table in the PostgreSQL database.
#
#         Parameters:
#         - table_name (str): The name of the table to truncate.
#         """
#         query = f"TRUNCATE TABLE {table_name} CASCADE;"
#         try:
#             self.execute_query(query)
#             logging.info(f"Table '{table_name}' truncated successfully.")
#         except psycopg2.Error as e:
#             logging.error(f"Error truncating table '{table_name}': {e}")
#             raise
#
#     def upsert_data(self, table_name, data, unique_columns):
#         """
#         Upserts data into the specified table. If a record with the same unique
#         identifiers already exists, it updates the record; otherwise, it inserts a new record.
#
#         Parameters:
#         - table_name (str): The name of the table to upsert data into.
#         - data (list of dict): A list of dictionaries, where each dictionary represents a row to upsert.
#         - unique_columns (list of str): A list of column names that uniquely identify a row.
#         """
#         if not data:
#             logging.warning("No data to upsert.")
#             return
#
#         columns = list(data[0].keys())
#         columns_str = ", ".join(columns)
#         placeholders_str = ", ".join(["%s"] * len(columns))
#         unique_columns_str = ", ".join(unique_columns)
#         update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns])
#
#         query = f"""
#             INSERT INTO {table_name} ({columns_str})
#             VALUES ({placeholders_str})
#             ON CONFLICT ({unique_columns_str})
#             DO UPDATE SET {update_str};
#         """
#
#         try:
#             with self.conn.cursor() as cur:
#                 for row in data:
#                     values = [row[col] for col in columns]
#                     cur.execute(query, values)
#                 self.conn.commit()
#             logging.info(f"Successfully upserted {len(data)} records into '{table_name}'.")
#         except psycopg2.Error as e:
#             self.conn.rollback()
#             logging.error(f"Upsert error: {e}")
#             raise
#
# # Example Usage:
# if __name__ == '__main__':
#     # Database credentials
#     dbname = "product-search-data"  # Replace with your database name
#     user = "postgres"  # Replace with your username
#     password = "root"  # Replace with your password
#     host = "35.184.42.158"  # Public IP address
#     port = 5432  # Default PostgreSQL port
#
#     # Initialize the database connection
#     db = PostgresDB(dbname, user, password, host, port)
#
#     try:
#         # Connect to the database
#         db.connect()
#
#         # Example 1: Truncate a table
#         # table_to_truncate = 'product-search-data'
#         # db.truncate_table(table_to_truncate)
#         #
#         # # Example 2: Upsert data into a table
#         # table_to_upsert = 'product-search-data'
#         # unique_columns = ['id']  # Replace with your unique column(s)
#         # data_to_upsert = [
#         #     {'id': 1, 'name': 'Product A', 'price': 25.00},
#         #     {'id': 2, 'name': 'Product B', 'price': 50.00},
#         #     {'id': 1, 'name': 'Product A Updated', 'price': 27.50}  # Updates existing record
#         # ]
#         # db.upsert_data(table_to_upsert, data_to_upsert, unique_columns)
#
#         columns_definition = """
#                     model SERIAL PRIMARY KEY,
#                     brand VARCHAR(255),
#                     price VARCHAR(255),
#                     details TEXT,
#                     features TEXT,
#                     insights TEXT,
#                     brand VARCHAR(255)
#                     Reviews Count, Battery Life, Weight, Special Features
#                     Already present: +ve, -ve, neutral
#                     Price, User Rating, Battery, Weight and Special Feature
#                 """
#
#         # Create a new table in the database
#         table_name = "product_data"
#         db.create_table(table_name, columns_definition)
#
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#
#     finally:
#         # Ensure the connection is closed
#         if db and db.conn:
#             db.close()