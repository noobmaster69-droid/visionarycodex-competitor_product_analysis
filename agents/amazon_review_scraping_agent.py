import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_amazon_reviews(product_url, num_pages=5):
    reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        product_id = re.search(r'/dp/([A-Z0-9]+)(?:/|\?)', product_url, re.IGNORECASE).group(1)
    except AttributeError:
        print("Invalid Amazon product URL.")
        return None

    for page_num in range(1, num_pages + 1):
        review_url = f"https://www.amazon.in/product-reviews/{product_id}/ref=cm_cr_arp_d_viewpnt_rgt?ie=UTF8&pageNumber={page_num}"

        try:
            response = requests.get(review_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            review_elements = soup.find_all('div', {'data-hook': 'review'})

            for review_element in review_elements:
                try:
                    rating = review_element.find('i', {'data-hook': 'review-star-rating'}).text.strip().split(' ')[0]
                    title = review_element.find('a', {'data-hook': 'review-title'}).text.strip()
                    body = review_element.find('span', {'data-hook': 'review-body'}).text.strip()
                    date = review_element.find('span', {'data-hook': 'review-date'}).text.strip()
                    reviews.append({
                        'rating': rating,
                        'title': title,
                        'body': body,
                        'date': date,
                    })
                except AttributeError:
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occured on page {page_num}: {e}")
            break
    return pd.DataFrame(reviews)

product_url = "https://www.amazon.in/Logitech-Wireless-Receiver-Ambidextrous-Compatible/dp/B0D18192T2/ref=sr_1_1?crid=KVCN5S0KFLAU&dib=eyJ2IjoiMSJ9.KCf1ecsc-dKb_wIkYiiKtI9x9wWny6rD6E1bD2dm_wVJRTOx0f57et5J9MjHdkYqV_h4aZUGQW1ZsnwOHlY9q5_yZsYQbf6DQLiRlv4s-tLIJr7bI2p3n4VBcmHljYXhUIZVtaYBdE-0VQ814nB8WMQL06Ebf9siw7NhhUpyBPqP87CQT4-kAVMtP1iWtvfQRSIXUNdsk83DhCRs4zk7L69fDJIDEBJft6USPrwj8pDC3qBPWRY1QouP5h-uiz2f4kzBuuZ6WqtHc8TMj_mFEd0suJUqWvw0SzSQdxHIg84JRCDjjzGH7pzRWIRbnxdKcwbd4g7BgpoQ8kNZ_P2NApoetfm8f-O9OrqM_ryXxWc.2oOfqcX7iLON5ZYNTNzadg32grZKRs_4bq7ziWxLvSo&dib_tag=se&keywords=Mouse&qid=1735125722&s=computers&sprefix=mous%2Ccomputers%2C236&sr=1-1&th=1"
df_reviews = scrape_amazon_reviews(product_url, num_pages=3)

if df_reviews is not None and not df_reviews.empty:
    print(df_reviews.head())
    df_reviews.to_csv("amazon_reviews.csv", index=False)
else:
    print("No reviews scraped or an error occurred.")