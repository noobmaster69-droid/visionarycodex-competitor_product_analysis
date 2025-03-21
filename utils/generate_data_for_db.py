import os
import json
from vertexai.generative_models import GenerativeModel
import vertexai

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")
vertexai.init(project=PROJECT_ID, location=LOCATION)
MODEL = GenerativeModel("gemini-1.5-pro-002")

expected_data = '[{"brand": "Apple", "model": "iPhone 15 Pro", "category": "electronics", "features": {"A17 Bionic Chip": true, "ProMotion Display": true, "Titanium Frame": true}, "insights": {"popularity": "Very High", "priceTrend": "Stable", "demand": "Extreme", "marketShare": "28%"}, "reviews": [{"user": "AppleFan123", "rating": 4.8, "comment": "Best iPhone yet", "date": "2024-03-18"}]}, {"brand": "OnePlus", "model": "12 Pro", "category": "electronics", "features": {"Snapdragon 8 Gen 3": true, "100W Fast Charging": true, "LTPO AMOLED": true}, "insights": {"popularity": "High", "priceTrend": "Decreasing", "demand": "High", "marketShare": "15%"}, "reviews": [{"user": "SpeedMaster", "rating": 4.6, "comment": "Blazing fast performance", "date": "2024-03-09"}]}]'

prompt = "Please generate five distinct models for each branch. The output much contain five brands in total, the models must be mobile phones only. The expected output is to be of this format:"+expected_data+" return it in such a way that it can be used as a python array consisting of these products. Meaning, I intend to use your response and copy paste it elsewhere and just use it as an object/variable, also ensure that the brand being fetched is not Google, Xiaomi, Samsung, Apple and OnePlus."
response_text = MODEL.generate_content(prompt).text
response_text = response_text[len('```json'):]
response_text = response_text[:-len('```')]
response_text.strip()
print(response_text)