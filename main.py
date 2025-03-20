import os
from serpapi_agent import SerpAPIAgent
from agents.google_scraper import search_google, generate_query
from scrape_immersive_data import scrape_immersive_data
from review_analysis import get_review_data

# Get product name from the user
product_name = input("Enter the product name: ")

# Get comma-separated company names from the user
company_names_input = input("Enter the company names (comma-separated): ")

# You can now use product_name and company_names for further processing
# search_google(product_name, company_names_input)


# Instantiate the SerpAPIAgent with the API key
api_key = os.getenv("SERPAPI_API_KEY")
serp_api_agent = SerpAPIAgent(api_key)

# Call to get scraped data from Google Shopping, specific to Amazon site
shopping_data = serp_api_agent.get_google_shopping_data(generate_query(product_name, company_names_input))
print(shopping_data)

immersive_data = scrape_immersive_data(shopping_data, api_key)
print(immersive_data)

review_data = get_review_data(shopping_data)

#Now, gotta get the reviews from Amazon
# print(get_review_data(shopping_data))
