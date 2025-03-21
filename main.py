from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.review_analysis import get_review_data, scrape_data_from_link
from agents.shopping_results_scraping_agent import scrape_shopping_data
from agents.pinecone_retrieval import retrieve_product
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch/")
async def analyze_product(product_name: str = Query(...), company_names_input: str = Query(...)):
    """
    Analyzes a product based on its name and company, returning a JSON response
    containing shopping data, review data, and other relevant information.
    """
    companies_to_search = []
    final_output = []
    companies = [word.strip() for word in company_names_input.split(',')]
    for company in companies:
        queried_output = retrieve_product(company)
        if queried_output is None:
            companies_to_search.append(company)
        else:
            final_output.append(queried_output)
    if(companies_to_search.count()==0):
        return final_output
    else:
        company_names_input = ", ".join(map(str, companies_to_search))
        google_shopping_data = scrape_shopping_data(product_name, company_names_input)
        product_screen_data = scrape_data_from_link(google_shopping_data)
        review_data = get_review_data(product_screen_data)

        try:
            shopping_results = json.loads(google_shopping_data)['shopping_results']
            review_data_json = json.loads(review_data)
            for i in range(len(shopping_results)):  # Use shopping_results instead of google_shopping_data
                item_name = shopping_results[i]['title']
                parts = item_name.split(' ', 1)
                brand = parts[0]
                model = parts[1]
                product_details = {
                    "brand": brand,
                    "model": model,
                    "category": product_name,
                    "good_features": review_data_json[i]["good_features"],
                    "bad_features": review_data_json[i]["bad_features"],
                    "other_data": product_screen_data[i],
                    "summary": review_data_json[i]["summary"]
                }
                final_output.append(product_details)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return final_output