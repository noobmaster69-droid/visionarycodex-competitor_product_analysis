import json
import requests
import os

def scrape_immersive_data(shopping_data, serpapi_key):
    """
    Scrapes data from the serpapi_immersive_product_api for each product in shopping_data.
    """
    results = []
    data = json.loads(shopping_data)
    for product in data:
        immersive_api_url = product.get('serpapi_immersive_product_api')
        if immersive_api_url:
            try:
                # Add the SerpAPI key to the URL
                url_with_key = f"{immersive_api_url}&api_key={serpapi_key}"
                response = requests.get(url_with_key)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                immersive_data = response.json()
                results.append(immersive_data)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {immersive_api_url}: {e}")
                results.append(None)
        else:
            print("serpapi_immersive_product_api URL not found for this product.")
            results.append(None)  # Append None if URL is missing
    return results

# shopping_data = """
# [
#     {
#         "position": 1,
#         "title": "Samsung Galaxy A16 5G Cell Phone",
#         "immersive_product_page_token": "eyJlaSI6IkNobmJaNHJvQmRxNGtQSVB2X21GNFE0IiwicHJvZHVjdGlkIjoiODA2MDYyNTQ0MTk3Njk3MTA4IiwiY2F0YWxvZ2lkIjoiIiwiaGVhZGxpbmVPZmZlckRvY2lkIjoiODA2MDYyNTQ0MTk3Njk3MTA4IiwiaW1hZ2VEb2NpZCI6IjkzODc4MjgzNzMxODE2MTM3MDQiLCJyZHMiOiJQQ18xMDI3Nzg5NzQ2MjQyOTY2NzMyNXxQUk9EX1BDXzEwMjc3ODk3NDYyNDI5NjY3MzI1IiwicXVlcnkiOiJCdXkrTW9iaWxlK1Bob25lcytmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6IiIsIm1pZCI6IiIsInB2dCI6ImhnIiwidXVsZSI6bnVsbH0=",
#         "serpapi_immersive_product_api": "https://serpapi.com/search.json?engine=google_immersive_product&page_token=eyJlaSI6IkNobmJaNHJvQmRxNGtQSVB2X21GNFE0IiwicHJvZHVjdGlkIjoiODA2MDYyNTQ0MTk3Njk3MTA4IiwiY2F0YWxvZ2lkIjoiIiwiaGVhZGxpbmVPZmZlckRvY2lkIjoiODA2MDYyNTQ0MTk3Njk3MTA4IiwiaW1hZ2VEb2NpZCI6IjkzODc4MjgzNzMxODE2MTM3MDQiLCJyZHMiOiJQQ18xMDI3Nzg5NzQ2MjQyOTY2NzMyNXxQUk9EX1BDXzEwMjc3ODk3NDYyNDI5NjY3MzI1IiwicXVlcnkiOiJCdXkrTW9iaWxlK1Bob25lcytmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6IiIsIm1pZCI6IiIsInB2dCI6ImhnIiwidXVsZSI6bnVsbH0%3D",
#         "product_link": "https://www.google.com/shopping/product/1?gl=us&prds=pid:806062544197697108",
#         "product_id": "806062544197697108",
#         "serpapi_product_api": "https://serpapi.com/search.json?engine=google_product&gl=us&google_domain=google.com&hl=en&product_id=806062544197697108",
#         "source": "Amazon.com",
#         "source_icon": "https://serpapi.com/searches/67db1909428cbfa5521b0993/images/b4ed7ccfbf4b167149746ff6958f315ca0638319e874902a5489284abc949186.png",
#         "price": "$174.99",
#         "extracted_price": 174.99,
#         "old_price": "$200",
#         "extracted_old_price": 200,
#         "rating": 4.4,
#         "reviews": 112000,
#         "snippet": "Quality camera (8,200 user reviews)",
#         "thumbnail": "https://serpapi.com/searches/67db1909428cbfa5521b0993/images/b4ed7ccfbf4b167149746ff6958f315c8a094e2db54a02212fef472597c48e1c.webp",
#         "thumbnails": [
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcRVYCRh16Jr0j38iYgeE-x8Q4612L8ydW0fA-SBm9SRufzH5hGT-qJhNI5mgzCOseN-qTDWBmJvvOcRFBpH5jI7ByguameQifE7I1oUftyghb_2QNG3WPqyHA",
#             "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRDxA8W-P66QEFcfWELQzZ-SnPah2QXBJDiLgiXzYrnKyc9uhtsYr3bjzIZHDdqSBf773vvqDO1ARp4wr21f3lqSebheqYZGhkCDZAB9NziLRwws50SDkUA",
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcReX6hxINsQguUE2O-9YQFI8tpzNa-vSd101bcheQjnnIvDOaYobnp3ju3JpFRT-pMmWMeaF0XFddy7jDFE4EONw2bZaqCwIXQsi5e_mWST6_inswK15QdL",
#             "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcTAaVP7T4zY659h6MObmijgBtKlAuHCjG2yXEbQ49lBMktkCYTyOFnqU0JZgflcAGe-bmZIlj_byQpFiDOi_TME-jgHsZqJahLXQjMOz5B6wum_amT5cATM",
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTgcVRzLLNEgV0d4ePiPWX4VN0OPQKxqF4WM3jTU7EXmSlG8q5I2ckLYoUS1dBRxq8QfQuh86Y-jB22tUvgR2QDIunybKowD1Fo0Q5OK0OLLYN1AnB2SJwhcQ"
#         ],
#         "tag": "12% OFF",
#         "extensions": [
#             "12% OFF"
#         ],
#         "delivery": "Free delivery"
#     },
#     {
#         "position": 2,
#         "title": "Samsung Galaxy S24 FE",
#         "product_link": "https://www.google.com/shopping/product/14014316003760913604?gl=us",
#         "product_id": "14014316003760913604",
#         "serpapi_product_api": "https://serpapi.com/search.json?engine=google_product&gl=us&google_domain=google.com&hl=en&product_id=14014316003760913604",
#         "immersive_product_page_token": "eyJlaSI6IkNobmJaNHJvQmRxNGtQSVB2X21GNFE0IiwicHJvZHVjdGlkIjoiIiwiY2F0YWxvZ2lkIjoiMTQwMTQzMTYwMDM3NjA5MTM2MDQiLCJoZWFkbGluZU9mZmVyRG9jaWQiOiIxMDQ2NjU0MTU5MTIyMDI1NDA5NyIsImltYWdlRG9jaWQiOiIxNzE3ODY0MzMzNzY5NTM0NTkzNyIsInJkcyI6IlBDXzg4ODgyOTc5MDA5ODA0MjI5MTV8UFJPRF9QQ184ODg4Mjk3OTAwOTgwNDIyOTE1IiwicXVlcnkiOiJCdXkrTW9iaWxlK1Bob25lcytmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6Ijg4ODgyOTc5MDA5ODA0MjI5MTUiLCJtaWQiOiI1NzY0NjI3OTYxNTg3Mzg3MjgiLCJwdnQiOiJoZyIsInV1bGUiOm51bGx9",
#         "serpapi_immersive_product_api": "https://serpapi.com/search.json?engine=google_immersive_product&page_token=eyJlaSI6IkNobmJaNHJvQmRxNGtQSVB2X21GNFE0IiwicHJvZHVjdGlkIjoiIiwiY2F0YWxvZ2lkIjoiMTQwMTQzMTYwMDM3NjA5MTM2MDQiLCJoZWFkbGluZU9mZmVyRG9jaWQiOiIxMDQ2NjU0MTU5MTIyMDI1NDA5NyIsImltYWdlRG9jaWQiOiIxNzE3ODY0MzMzNzY5NTM0NTkzNyIsInJkcyI6IlBDXzg4ODgyOTc5MDA5ODA0MjI5MTV8UFJPRF9QQ184ODg4Mjk3OTAwOTgwNDIyOTE1IiwicXVlcnkiOiJCdXkrTW9iaWxlK1Bob25lcytmcm9tK0FtYXpvbiUzQSthcHBsZSUyQ3NhbXN1bmciLCJncGNpZCI6Ijg4ODgyOTc5MDA5ODA0MjI5MTUiLCJtaWQiOiI1NzY0NjI3OTYxNTg3Mzg3MjgiLCJwdnQiOiJoZyIsInV1bGUiOm51bGx9",
#         "source": "Amazon.com - Seller",
#         "source_icon": "https://serpapi.com/searches/67db1909428cbfa5521b0993/images/b4ed7ccfbf4b167149746ff6958f315ce153c752c0835fabe94ba267146ac4de.png",
#         "price": "$391.80",
#         "extracted_price": 391.8,
#         "second_hand_condition": "refurbished",
#         "rating": 4.5,
#         "reviews": 50000,
#         "snippet": "Quality camera (5,857 user reviews)",
#         "thumbnail": "https://serpapi.com/searches/67db1909428cbfa5521b0993/images/b4ed7ccfbf4b167149746ff6958f315c641606a0fbf20fc86a2df5c217f50b97.webp",
#         "thumbnails": [
#             "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQkMJZjt8_kdi3mEG85EOi0y3baH0DmdILsTmogOsAphrS3YwQDAOf8gUtAo9p2qhZ_qn9iR7_P82imeM8kBAm1YvNVylja0hg65zxKJgxi9x13FA7YlaA3",
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcRbXqsecTrfiSmv5J7f7kU5CqvzB70Tvl6FxxVgNZMhMPZ-_6V55fi39Z5Igpf9R1kXsh1QSlhuZLaXIvjE9DnJc9Kckpg_kKk3h7E-AdgPmjAWMb_WFCvG",
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcRssKWEYvSADBW8Zv26fGXOaheUlHXsTbB3frE55pUtmZ1ovodtcS9V0dbOHIsL52iba2hMurV3Sh9dj4syip3FRiFkpxH2T_SHv-Ur57YZeh3fcagcAvm0qQ",
#             "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRTp4RgZaboATkX7axGLO2FiQXEBzbeoPGLv725qr9Tz9uIhBirHnAuJtB9cscI1b1930Z_S_vkk7L87rpr31sNWsfF5wRvJwXfnmEJ0lLo7Kv1sGQ1tM0E8Q",
#             "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcQjNPGMLh88gv5y3YL9vnFTVW0ZFN0RD0ioeuxpfxxB4KABp9Dk4g881kYNHgfTy2psRcKAcfbno312m-gNN4WYxxg8CBH_uTassDRzoluxVKGwtByU1cef"
#         ],
#         "tag": "30% OFF",
#         "extensions": [
#             "30% OFF"
#         ],
#         "delivery": "Free delivery"
#     }
# ]
# """
#
# # Replace 'YOUR_SERPAPI_KEY' with your actual SerpAPI key
# immersive_data_list = scrape_immersive_data(shopping_data, "869addb59bc8e79c129a2317fb5104536dc9ebcae75b93687ee22b587fce6154")
#
# # Print the scraped data
# for data in immersive_data_list:
#     if data:
#         print(json.dumps(data, indent=2))
#     else:
#         print("Failed to retrieve immersive data for this product.")