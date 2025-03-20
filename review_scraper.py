# pip install requests
import requests

# set up the URL and API key
url = 'https://www.amazon.com/Casio-MDV106-1AV-Analog-Watch-Black/dp/B009KYJAJY/?_encoding=UTF8&pd_rd_w=UdQTG&content-id=amzn1.sym.4bba068a-9322-4692-abd5-0bbe652907a9&pf_rd_p=4bba068a-9322-4692-abd5-0bbe652907a9&pf_rd_r=ERVPNH232KXYXFNGFXA5&pd_rd_wg=aY8V4&pd_rd_r=fd99159b-9d08-4162-9582-bc34b28fac83&ref_=pd_hp_d_btf_nta-top-picks&th=1'
apikey ="7b6f670b465d6f822c3156323d3ca960cf055774"

# parameters for the API request
params = {
    'url': url,
    'apikey': apikey,
    'css_extractor': """{
        "reviewer_name": "span.a-profile-name",
        "review_title": "a.review-title",
        "review_date": "span.review-date",
        "review_text": "span.review-text",
        "review_rating": "i.review-rating",
        "review_image": "img.review-image-tile @src"
    }"""
}

# make the API request
response = requests.get('https://api.zenrows.com/v1/', params=params)

# print the response
print(response.text)
