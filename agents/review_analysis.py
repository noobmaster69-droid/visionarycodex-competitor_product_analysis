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
    # prompt = prompt + " Provide the output in a JSON String format, where the Key's are the 'title' and the values being the 'good_features', 'bad_features', and 'summary' of the product."
    response_text = MODEL.generate_content(prompt).text
    response_text = response_text[len('```json'):]
    response_text = response_text[:-len('```')]
    response_text.strip()
    json_objects = json.loads(response_text)
    return json.dumps(json_objects, indent=2)
def get_review_data(input_data):

    # Enhanced for loop to iterate through the list and analyze each product
    prompt = ""
    # data = json.loads(input_data)
    # shopping_results = data['shopping_results']
    product_number = 1
    for product_data in input_data:
        prompt = prompt + construct_prompt(product_data, product_number)
        product_number = product_number + 1
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

def scrape_data_from_link(input_data):
    data = json.loads(input_data)
    shopping_results = data['shopping_results']
    scraped_data = []
    for product_data in shopping_results:
        link = product_data['scrapingdog_product_link']
        # Fetch the JSON data from the serpapi_product_api link
        response = requests.get(link)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        product_details = json.loads(response.content)
        scraped_data.append(product_details)
    return scraped_data

#Need to have data mocked. Need to change it from using data, and instead provide the output.
def construct_prompt(product_details, product_number):
    # link = data['scrapingdog_product_link']
    # Fetch the JSON data from the serpapi_product_api link
    # response = requests.get(link)
    # response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    # product_details = json.loads(response.content)

    # Extract review filters and sort by count in descending order
    if 'reviews_results' in product_details and 'topics' in product_details['reviews_results']:
        filters = product_details['reviews_results']['topics']
        sorted_filters = sorted(filters, key=lambda x: x['mentions'], reverse=False)
        top_10_filters = sorted_filters[:10]

        # Extract filter labels for the top 10 filters
        top_10_filter_labels = [f["keyword"] for f in top_10_filters]
        filter_labels = [f["keyword"] for f in top_10_filters]
        product_name = product_details['product_results']['title']

        # Prompt to identify good and bad features and generate a summary
        return (
            f"The product number {product_number} is {product_name}. Top filters from customer reviews include: {', '.join(filter_labels)}.  "
            f"Identify the good features, bad features and give a one to two line summary of the product based "
            f"on these filters. Return as a List which contains elements of the following format: {{ \"product_name\": product_name, \"good_features\": [good features], \"bad_features\": [bad features], "
            f"\"summary\": summary, \"product_number\": product_number}}.")