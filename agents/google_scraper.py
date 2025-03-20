import requests
import urllib.parse

def search_google(product_name, companies_list):
    query = generate_query(product_name, companies_list)
    encoded_query = urllib.parse.quote_plus(query)
    api_endpoint = f"https://serp.api.zenrows.com/v1/targets/google/search/{encoded_query}"
    params = {
        "apikey": "7b6f670b465d6f822c3156323d3ca960cf055774",
    }
    response = requests.get(api_endpoint, params=params)
    print("\nResponse.json:", response.json())
    return response.text


"""This is used for generating the google query text"""
def generate_query(product_name, input_string):
    """
    Lowercases, trims spaces, and creates a comma-separated string,
    prefixed with the product name.

    Args:
        product_name: The name of the product category.
        input_string: The input string containing brands.

    Returns:
        A string formatted as "product_name: brand1,brand2,brand3".
    """
    brands = input_string.split(',')  # Split into a list
    formatted_brands = []

    for brand in brands:
        trimmed_brand = brand.strip().lower()  # Trim spaces and lowercase
        formatted_brands.append(trimmed_brand)

    return f"{"Buy "+product_name+" from Amazon"}: " + ','.join(formatted_brands)  # Join into a string and add prefix