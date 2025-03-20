import serpapi
import json
import os
# from utils.logger import setup_logger
from dotenv import load_dotenv
load_dotenv()
# logger = setup_logger('serpapi_agent', 'logs/serpapi_agent.log')

api_key = os.getenv("SERPAPI_API_KEY")
client = serpapi.Client(api_key=api_key)


class SerpAPIAgent:
    def __init__(self, api_key):
        self.api_key = api_key
    def get_google_shopping_data(self, product_query):
        """Fetches product data from Google Shopping using SerpAPI."""
        results = client.search({'engine': 'google_shopping',
                                 'q': product_query,
                                 'gl': 'us',
                                 'hl': 'en',
                                 'num': 5
                                 })
        shopping_results = results.get('shopping_results', [])
        shopping_data_json = json.dumps(shopping_results, indent=4)
        #
        # if len(shopping_results) == 0:
        #     print('No results found')
        # else:
        #     count = 0
        #     for product in shopping_results:
        #         print(f"Product: {product['title']}")
        #         print(f"Price: {product['price']}")
        #         print(f"Store: {product['source']}")
        #         print('Thumbnail:', product['thumbnail'])
        #         print('Price:', product['price'])
        #         if 'Rating' in product:
        #             print('Rating:', product['rating'])
        #         if 'extensions' in product:
        #             print('Extensions:', product['extensions'])
        #         print('-------------------')
        #         count += 1
        #         if count >= 5:
        #             break
        return shopping_data_json