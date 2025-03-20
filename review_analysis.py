import os
import json
from vertexai.generative_models import GenerativeModel
import vertexai
import requests
import re
from dotenv import load_dotenv

load_dotenv()

# Vertex AI setup
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")
vertexai.init(project=PROJECT_ID, location=LOCATION)
MODEL = GenerativeModel("gemini-1.5-pro-002")

# SerpAPI key
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

# This function is used to analyze product reviews from the SERPAPI output, this uses the Vertex AI model to generate a summary of the reviews
def analyze_product_reviews(prompt):
    """
    Analyzes product reviews, extracts top filters, and generates a summary using Vertex AI.
    Returns a JSON object with 'good_features', 'bad_features', and 'summary' keys.
    """
    # Extract review filters and sort by count in descending order
    response_text = MODEL.generate_content(prompt).json
    return response_text
    #     if 'reviews_results' in product_details and 'filters' in product_details['reviews_results']:
    #         filters = product_details['reviews_results']['filters']
    #         sorted_filters = sorted(filters, key=lambda x: x['count'], reverse=True)
    #         top_10_filters = sorted_filters[:10]
    #
    #         # Extract filter labels for the top 10 filters
    #         top_10_filter_labels = [f["label"] for f in top_10_filters]
    #
    #         # Generate a summary of the product based on the top 5 filters
    #         top_5_filters = sorted_filters[:5]
    #         filter_labels = [f["label"] for f in top_5_filters]
    #         product_name = product_data['title']
    #
    #         # Prompt to identify good and bad features and generate a summary
    #         prompt = (f"The product is {product_name}. Top filters from customer reviews include: {', '.join(filter_labels)}.  "
    #                   f"Identify the good features, bad features and give a one to two line summary of the product based "
    #                   f"on these filters. Return in JSON format: {{\"good_features\": [good features], \"bad_features\": [bad features], "
    #                   f"\"summary\": summary, \"title\": product_name}}.")
    #
    #         response_text = MODEL.generate_content(prompt).text
    #
    #         # Parse the JSON response
    #         try:
    #             response_text = re.sub(r'^\s*```json\s*', '', response_text)
    #             response_text = re.sub(r'\s*```\s*$', '', response_text)
    #             response_json = json.loads(response_text)
    #             good_features = response_json.get('good_features', [])
    #             bad_features = response_json.get('bad_features', [])
    #             summary = response_json.get('summary', '')
    #             title = response_json.get('title', '')
    #         except (json.JSONDecodeError, TypeError):
    #             good_features = []
    #             bad_features = []
    #             summary = response_text  # Use the raw response if JSON parsing fails
    #             title = product_name
    #
    #         # Create the JSON object
    #         result = {
    #             'good_feature': good_features,
    #             'bad_feature': bad_features,
    #             'summary': summary,
    #             'title': title
    #         }
    #         return json.dumps(result)
    #     else:
    #         return json.dumps({'good_feature': [], 'bad_feature': [], 'summary': "No review filters found in the product details."})
    #
    # except requests.exceptions.RequestException as e:
    #     return json.dumps({'good_feature': [], 'bad_feature': [], 'summary': f"Error fetching data from URL: {str(e)}"})
    # except json.JSONDecodeError:
    #     return json.dumps({'good_feature': [], 'bad_feature': [], 'summary': "Error decoding JSON."})
    # except Exception as e:
    #     return json.dumps({'good_feature': [], 'bad_feature': [], 'summary': f"An error occurred: {str(e)}"})

def get_review_data(serpapi_data):
    data = json.loads(serpapi_data)
    # Enhanced for loop to iterate through the list and analyze each product
    prompt = ""
    product_number = 1
    for product_data in data:
        # product_data = clean_json_string(product_data)
        construct_prompt(product_data, prompt, product_number)
        product_number = product_number + 1
        if product_number == 11:
            break
    results = analyze_product_reviews(prompt)
    return results

def clean_json_string(json_string):
    """
    Cleans a JSON string by removing control characters and ensuring proper escaping.
    """
    # Remove control characters
    cleaned_string = re.sub(r'[\x00-\x1F]', '', json_string)

    # Ensure backslashes are properly escaped
    cleaned_string = cleaned_string.replace('\\', '\\\\')

    return cleaned_string


def construct_prompt(serpapi_data, prompt, product_number):
    # Extract the serpapi_product_api link
    product_api_link = serpapi_data['serpapi_product_api']

    # Add the SerpAPI key to the URL
    product_api_link += f"&api_key={SERPAPI_KEY}"

    # Fetch the JSON data from the serpapi_product_api link
    response = requests.get(product_api_link)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    product_details = response.json()

    # Extract review filters and sort by count in descending order
    if 'reviews_results' in product_details and 'filters' in product_details['reviews_results']:
        filters = product_details['reviews_results']['filters']
        sorted_filters = sorted(filters, key=lambda x: x['count'], reverse=True)
        top_10_filters = sorted_filters[:10]

        # Extract filter labels for the top 10 filters
        top_10_filter_labels = [f["label"] for f in top_10_filters]
        filter_labels = [f["label"] for f in top_10_filters]
        product_name = serpapi_data['title']

        # Prompt to identify good and bad features and generate a summary
        prompt = prompt + (
            f"The product number {product_number} is {product_name}. Top filters from customer reviews include: {', '.join(filter_labels)}.  "
            f"Identify the good features, bad features and give a one to two line summary of the product based "
            f"on these filters. Return in JSON format: {{\"good_features\": [good features], \"bad_features\": [bad features], "
            f"\"summary\": summary, \"title\": product_name, \"product_number\": product_number}}.")

# json_string = """
# [
#     {
#         "position": 40,
#         "title": "Samsung Galaxy S22",
#         "product_link": "https://www.google.com/shopping/product/12179345341619100142?gl=us",
#         "product_id": "12179345341619100142",
#         "serpapi_product_api": "https://serpapi.com/search.json?engine=google_product&gl=us&google_domain=google.com&hl=en&product_id=12179345341619100142",
#         "immersive_product_page_token": "eyJlaSI6IktfYmFaNzZlQXNxaDVOb1B3LTZta0FnIiwicHJvZHVjdGlkIjoiIiwiY2F0YWxvZ2lkIjoiMTIxNzkzNDUzNDE2MTkxMDAxNDIiLCJoZWFkb
# GluZU9mZmVyRG9jaWQiOiIxMTI2Mjk4NzgxMzU4MDI0MzczOSIsImltYWdlRG9jaWQiOiI2MDI0NDk5NDQ1NjM0MjE1Nzc0IiwicmRzIjoiUENfMTA1MDcwNzQ5MjE0MzM2MzQ5Nzd8UFJPRF9QQ18xMDUwNzA
# 3NDkyMTQzMzYzNDk3NyIsInF1ZXJ5IjoiQnV5K01vYmlsZStQaG9uZStmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6IjEwNTA3MDc0OTIxNDMzNjM0OTc3IiwibWlkIjoiNTc2NDYyNjA1MTIwNjg0ODg1IiwicHZ0IjoiaGciLCJ1dWxlIjpudWxsfQ==",
#         "serpapi_immersive_product_api": "https://serpapi.com/search.json?engine=google_immersive_product&page_token=eyJlaSI6IktfYmFaNzZlQXNxaDVOb1B3LTZta0FnI
# iwicHJvZHVjdGlkIjoiIiwiY2F0YWxvZ2lkIjoiMTIxNzkzNDUzNDE2MTkxMDAxNDIiLCJoZWFkbGluZU9mZmVyRG9jaWQiOiIxMTI2Mjk4NzgxMzU4MDI0MzczOSIsImltYWdlRG9jaWQiOiI2MDI0NDk5NDQ
# 1NjM0MjE1Nzc0IiwicmRzIjoiUENfMTA1MDcwNzQ5MjE0MzM2MzQ5Nzd8UFJPRF9QQ18xMDUwNzA3NDkyMTQzMzYzNDk3NyIsInF1ZXJ5IjoiQnV5K01vYmlsZStQaG9uZStmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6IjEwNTA3MDc0OTIxNDMzNjM0OTc3IiwibWlkIjoiNTc2NDYyNjA1MTIwNjg0ODg1IiwicHZ0IjoiaGciLCJ1dWxlIjpudWxsfQ%3D%3D",
#         "source": "Amazon.com - Seller",
#         "source_icon": "https://encrypted-tbn2.gstatic.com/favicon-tbn?q=tbn%3AANd9GcT0TsMMuS8IRIUU_Envbo02npaZ6DJgbXTwa-h2DSMswBydNyxi_1NukUkPuQPc8-6EH8dopTDEyU5ccMeLEvcSrbCBtAW3",
#         "price": "$246.69",
#         "extracted_price": 246.69,
#         "second_hand_condition": "refurbished",
#         "rating": 4.2,
#         "reviews": 22000,
#         "snippet": "Quality camera (1,683 user reviews)",
#         "thumbnail": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQFgermLl49uHGAT6wdjAAbH-EtO78Y7FoO0myiLdIrCiF1yuehz1XpYCcidICir2saNM0DtZqluMiXULdauoDpMzO52oEVQrINFTRwqSY",
#         "thumbnails": [
#             "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcS6v0SHkccWYK3Z6HrFHkzZQttpJSRfchn_VxFJckPBTo4Bpw7Aza8ulLhWrmtaKL5DuXX_P65cswKRzHSfA0UNWuLQ2bkM5sTSpPBblmQ"
#         ],
#         "tag": "-5%",
#         "extensions": [
#             "-5%"
#         ],
#         "delivery": "Free delivery"
#     }
# ]
# """
#
# data = json.loads(clean_json_string(json_string))
#
# for product in data:
#     print(analyze_product_reviews(product))