
import requests

api_key = "67e19fc7eccb45caac0ab4bb"

def search_amazon_for_asin(query):
    params = {
        "api_key": api_key,
        "query": "",
        "page": "1",
        "domain": "com",
        "country": "us",
        "postal_code": ""
    }

    response = requests.get("https://api.scrapingdog.com/amazon/search", params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")

def scrape_reviews(asin):
    params = {
        "api_key": api_key,
        "asin": asin,
        "domain": "com",
        "page": "1"
    }

    response = requests.get("https://api.scrapingdog.com/amazon/reviews", params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")