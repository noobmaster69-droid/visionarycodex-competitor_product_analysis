from agents.amazon_reviews_scraper import search_amazon_for_asin, scrape_reviews
from agents.gsmarena_scraping import scrape_data_from_gsmarena
from utils.generate_data_for_db import get_feature_importance
import re
import urllib.parse

def get_metadata(id, myBrand, product_screen_data, shopping_results, review_data_json):
    features = get_features(id, product_screen_data, shopping_results, review_data_json)
    insights = get_insights(id, product_screen_data, shopping_results, review_data_json)
    reviews = get_reviews(id, product_screen_data, shopping_results)
    details = get_details(id, product_screen_data, shopping_results, review_data_json, reviews)

    if 'title' in shopping_results:
        company_name = shopping_results['title'].split()[0]
    else:
        company_name = None  # Handle the case where 'title' is missing

    if company_name == myBrand:
        isMyCompany = True
    else:
        isMyCompany = False
    output = {
        "id": id,
        "competitorName": company_name,
        "isMyCompanyProduct": isMyCompany,
        "features": features,
        "insights": insights,
        "reviews": reviews,
        "details": details
    }
    return output

def get_features(id, product_screen_data, shopping_results, review_data_json):
    features = scrape_data_from_gsmarena(shopping_results['title'])
    features['thumbnail'] = product_screen_data[id]["product_results"]["media"][0]["link"]
    return features

def get_insights(id, product_screen_data, shopping_results, review_data_json):
    id = id
    product_screen_data = product_screen_data

    shopping_results = shopping_results
    review_data_json = review_data_json
    # prompts:
    # base price = product_screen_data[1]['online_sellers'][0]['base_price']
    prompt = "Based on these data points, provide insights on the product's popularity, price trend, demand, and availability. "
    prompt = prompt + "Base Price: " + str(product_screen_data[1]['online_sellers'][0]['base_price'])
    prompt = prompt + "Total Price: " + str(product_screen_data[1]['online_sellers'][0]['total_price'])
    prompt = prompt + "Available Prices: "
    for i in range(0, product_screen_data[1]['product_results']['prices'].__len__()):
        prompt = prompt + str(product_screen_data[1]['online_sellers'][i]['total_price'])
        if i!=product_screen_data[1]['product_results']['prices'].__len__()-1:
            prompt = prompt + ", "


    insights = {
        "popularity": "High",
        "priceTrend": "Stable",
        "demand": "High",
        "availability": "Available in stores",
    }
    return insights

# //Done
def get_reviews(id, product_screen_data, shopping_results ):
    reviews = {}
    online_sellers = asin = product_screen_data['online_sellers']
    for seller in online_sellers:
        if 'name' in seller and 'Amazon' in seller['name']:
            asin = get_asin_from_shopping_data(seller['link'])
            if asin is not None:
                reviews = scrape_reviews(asin)
            else:
                asin = search_amazon_for_asin(shopping_results['title'])
                reviews = scrape_reviews(asin)
        else:
            asin = search_amazon_for_asin(shopping_results['title'])
            reviews = scrape_reviews(asin)
    return reviews

def get_details(id, product_screen_data, shopping_results, review_data_json, reviews):
    id = id
    product_screen_data = product_screen_data['product_results']
    shopping_results = shopping_results
    review_data_json = review_data_json
    details = {
        "price": product_screen_data['prices'],
        "userRating": product_screen_data['rating'],
        "numberOfReviews": product_screen_data['reviews'],
        "specialFeatures": product_screen_data['features'],
        "reviewSentiment": get_review_sentiment(product_screen_data),
        "featureImportance": get_feature_importance(product_screen_data['prices'], product_screen_data['rating'], product_screen_data['features'], shopping_results['title']),

    }
    return details

# //Done
def get_review_sentiment(product_screen_data):
    # Need to implement this function
    positive = 0;
    negative = 0;
    neutral = 0;
    for i in range (product_screen_data['reviews_results']['ratings']):
        if 'reviews_results' in product_screen_data and 'ratings' in product_screen_data['reviews_results']:
            for i in range(len(product_screen_data['reviews_results']['ratings'])):
                if product_screen_data['reviews_results']['ratings'][i]['name'] in [5, 4]:
                    positive = positive + product_screen_data['reviews_results']['ratings'][i]['amount']
                elif product_screen_data['reviews_results']['ratings'][i]['name'] in [2, 1]:
                    negative = negative + product_screen_data['reviews_results']['ratings'][i]['amount']
                else:
                    neutral = neutral + product_screen_data['reviews_results']['ratings'][i]['amount']
    total = positive + negative + neutral
    positive = str(float(positive/total))+"%"
    negative = str(float(negative / total)) + "%"
    neutral = str(float(neutral / total)) + "%"
    reviewSentiment = {
        "positive" : positive,
        "negative" : negative,
        "neutral" : neutral
    }
    return reviewSentiment

def get_asin_from_shopping_data(url):
    try:
        # Check if it's a Google redirect and extract the actual URL
        if "google.com/url?" in url:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if "q" in query_params:
                url = query_params["q"][0]  # get the first url from the list.

        # Use a regular expression to find the ASIN
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", url)
        if asin_match:
            return asin_match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error extracting ASIN: {e}")
        return None