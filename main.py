from collections import defaultdict
from importlib.metadata import metadata

from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from agents.review_analysis import get_review_data, scrape_data_from_link
from agents.shopping_results_scraping_agent import scrape_shopping_data
from agents.pinecone_retrieval import retrieve_product_by_brand
from utils.data_upload_to_vector_db import upsert_data, upsert_data_new
from agents.visualization_agent import fetch_and_upload_in_batches
from typing import List
from utils.retrieve_metadata import get_metadata
from utils.generate_data_for_db import get_insights, get_company_details
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# def rundown(category_name, brand_name, company_names_input):
#     # company_names_input = ", ".join(map(str, companies_to_search))
#     """
#         Analyzes a product based on its name and company, returning a JSON response
#         containing shopping data, review data, and other relevant information.
#         """
#     companies_to_search = []
#     company_names_input = ', '.join(map(str, company_names_input))
#     final_output = []
#     # companies = [word.strip() for word in company_names_input.split(',')]
#     # for company in companies:
#     #     # queried_output = retrieve_product(company)
#     #     queried_output = retrieve_product_by_brand(company)
#     #     if queried_output is None:
#     #         companies_to_search.append(company)
#     #     else:
#     #         final_output.append(queried_output)
#     # if (companies_to_search.__len__() == 0):
#     #     return final_output
#     # else:
#     # company_names_input = ", ".join(map(str, companies_to_search))
#     google_shopping_data = scrape_shopping_data(category_name, company_names_input)
#     product_screen_data = scrape_data_from_link(google_shopping_data)
#     review_data = get_review_data(product_screen_data)
#
#     try:
#         shopping_results = json.loads(google_shopping_data)['shopping_results']
#         review_data_json = json.loads(review_data)
#         for i in range(len(shopping_results)):  # Use shopping_results instead of google_shopping_data
#
#             meta_data = get_metadata(i, brand_name, product_screen_data, shopping_results, review_data_json)
#             upsert_data_new(meta_data)
#             meta_data["id"] = i
#             final_output.append(meta_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return final_output
#
# brands = ["Realme"]
# print(rundown("MobilePhones", "Oppo", brands))

@app.get("/fetch-products/")
async def analyze_product(product_name: str = Query(...), brand_name: str = Query(...), company_names_input: str = Query(...)):
    """
    Analyzes a product based on its name and company, returning a JSON response
    containing shopping data, review data, and other relevant information.
    """
    companies_to_search = []
    final_output = []
    companies = [word.strip() for word in company_names_input.split(',')]
    for company in companies:
        # queried_output = retrieve_product(company)
        queried_output = retrieve_product_by_brand(company)
        if queried_output is None:
            companies_to_search.append(company)
        else:
            final_output.append(queried_output)
    if (companies_to_search.__len__() == 0):
        return final_output
    else:
        google_shopping_data = scrape_shopping_data(product_name, company_names_input)
        product_screen_data = scrape_data_from_link(google_shopping_data)
        review_data = get_review_data(product_screen_data)

        try:
            shopping_results = json.loads(google_shopping_data)['shopping_results']
            review_data_json = json.loads(review_data)
            for i in range(len(shopping_results)):  # Use shopping_results instead of google_shopping_data

                meta_data = get_metadata(i, brand_name, product_screen_data, shopping_results, review_data_json)
                upsert_data_new(meta_data)
                meta_data["id"] = i
                final_output.append(meta_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return final_output

@app.post("/update/")
async def update_products(product_names: List[str]):
    if not product_names:
        raise HTTPException(status_code=400, detail="Product list cannot be empty")
    fetch_and_upload_in_batches(product_names)
    return {"message": "Products updated successfully", "products": product_names}

@app.get("/fetch-categories/")
async def fetch_categories():
    response = {
        "success": True,
        "message": "Category fetch successful",
        "categories": [
            {"id": 1, "categoryName": "electronics"},
            {"id": 2, "categoryName": "fashion"},
            {"id": 3, "categoryName": "home"},
            {"id": 4, "categoryName": "beauty"},
            {"id": 5, "categoryName": "sports"}
        ]
    }
    return response

@app.post("/fetch-competitors/")
async def fetch_competitors(request_body: dict = Body(...)):
    category_name = request_body.get("category_name")
    brand_name = request_body.get("brand_name")
    try:
        response = get_company_details(category_name, brand_name)
    except Exception as e:
        response = {
            "success": False,
            "message": "Competitors fetch unsuccessful",
            "competitors": []
        }
        return response
    return response