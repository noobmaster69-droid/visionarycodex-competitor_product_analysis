from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from pinecone import Pinecone, ServerlessSpec
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'formal-loop-452705-h1'
REGION = 'us-central1'
PINECONE_API_KEY = 'pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i'
PINECONE_ENV = "us-east1"  # Or "us-west1-gcp" or your env
INDEX_NAME = "product-index"

# Sample data for recipes
products = [
    {"brand": "Samsung", "model": "Galaxy S24+", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Dynamic AMOLED 2X": True, "Enhanced Telephoto Lens": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "18%"}, "reviews": [{"user": "TechEnthusiast", "rating": 4.6, "comment": "Great all-around phone", "date": "2024-03-05"}]},
    {"brand": "Samsung", "model": "Galaxy S24", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Dynamic AMOLED 2X": True, "Triple Camera System": True}, "insights": {"popularity": "Medium", "priceTrend": "Stable", "demand": "Medium", "marketShare": "12%"}, "reviews": [{"user": "SamsungFan", "rating": 4.4, "comment": "Solid performance", "date": "2024-03-10"}]},
    {"brand": "Samsung", "model": "Galaxy Z Fold5", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Foldable Dynamic AMOLED 2X": True, "S Pen Support": True}, "insights": {"popularity": "Medium", "priceTrend": "Stable", "demand": "Medium", "marketShare": "8%"}, "reviews": [{"user": "FoldableFanatic", "rating": 4.3, "comment": "The future is foldable", "date": "2024-03-15"}]},
    {"brand": "Samsung", "model": "Galaxy Z Flip5", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Foldable Dynamic AMOLED 2X": True, "Flex Mode": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "7%"}, "reviews": [{"user": "CompactLover", "rating": 4.2, "comment": "So pocketable", "date": "2024-03-20"}]},
    {"brand": "Google", "model": "Pixel 8 Pro", "category": "electronics", "features": {"Tensor G3": True, "Smooth Display": True, "Super Res Zoom": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "12%"}, "reviews": [{"user": "PixelPerfect", "rating": 4.8, "comment": "Best camera phone", "date": "2024-03-25"}]},
    {"brand": "Google", "model": "Pixel 8", "category": "electronics", "features": {"Tensor G3": True, "Smooth Display": True, "Night Sight": True}, "insights": {"popularity": "Medium", "priceTrend": "Stable", "demand": "Medium", "marketShare": "8%"}, "reviews": [{"user": "GoogleFan", "rating": 4.5, "comment": "Pure Android experience", "date": "2024-03-30"}]},
    {"brand": "Google", "model": "Pixel 7a", "category": "electronics", "features": {"Tensor G2": True, "90Hz Smooth Display": True, "Long-lasting Battery": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "6%"}, "reviews": [{"user": "ValueSeeker", "rating": 4.3, "comment": "Great value Pixel", "date": "2024-04-05"}]},
    {"brand": "Google", "model": "Pixel Fold", "category": "electronics", "features": {"Tensor G2": True, "Foldable OLED Display": True, "Dual Screen Experience": True}, "insights": {"popularity": "Low", "priceTrend": "Stable", "demand": "Low", "marketShare": "3%"}, "reviews": [{"user": "EarlyAdopter", "rating": 4.0, "comment": "Promising but pricey", "date": "2024-04-10"}]},
    {"brand": "Google", "model": "Pixel 7 Pro", "category": "electronics", "features": {"Tensor G2": True, "Smooth Display": True, "Macro Focus": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "4%"}, "reviews": [{"user": "CameraGuru", "rating": 4.7, "comment": "Still a great camera", "date": "2024-04-15"}]},
    {"brand": "OnePlus", "model": "12 Pro", "category": "electronics", "features": {"Snapdragon 8 Gen 3": True, "100W Fast Charging": True, "LTPO AMOLED": True}, "insights": {"popularity": "High", "priceTrend": "Decreasing", "demand": "High", "marketShare": "15%"}, "reviews": [{"user": "SpeedMaster", "rating": 4.6, "comment": "Blazing fast performance", "date": "2024-03-09"}]},
    {"brand": "OnePlus", "model": "12", "category": "electronics", "features": {"Snapdragon 8 Gen 3": True, "80W Fast Charging": True, "AMOLED": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "10%"}, "reviews": [{"user": "OnePlusLoyalist", "rating": 4.4, "comment": "Solid choice", "date": "2024-03-14"}]},
    {"brand": "OnePlus", "model": "Nord N30", "category": "electronics", "features": {"Snapdragon 695": True, "5000 mAh Battery": True, "90Hz AMOLED": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "7%"}, "reviews": [{"user": "BudgetGamer", "rating": 4.2, "comment": "Good for gaming on a budget", "date": "2024-03-19"}]},
    {"brand": "OnePlus", "model": "11", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "80W Fast Charging": True, "LTPO AMOLED": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "5%"}, "reviews": [{"user": "FormerFlagshipUser", "rating": 4.7, "comment": "Still a great phone", "date": "2024-03-24"}]},
    {"brand": "OnePlus", "model": "Nord CE 3 Lite", "category": "electronics", "features": {"Snapdragon 695": True, "108MP Camera": True, "90Hz LCD": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "3%"}, "reviews": [{"user": "CameraLover", "rating": 4.0, "comment": "Great camera for the price", "date": "2024-03-29"}]},
    {"brand": "Xiaomi", "model": "14 Pro", "category": "electronics", "features": {"Snapdragon 8 Gen 3": True, "120W Fast Charging": True, "120Hz AMOLED": True}, "insights": {"popularity": "High", "priceTrend": "Decreasing", "demand": "High", "marketShare": "18%"}, "reviews": [{"user": "XiaomiEnthusiast", "rating": 4.5, "comment": "Excellent value for money", "date": "2024-04-01"}]},
    {"brand": "Xiaomi", "model": "14", "category": "electronics", "features": {"Snapdragon 8 Gen 3": True, "67W Fast Charging": True, "120Hz AMOLED": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "12%"}, "reviews": [{"user": "TechSavvy", "rating": 4.3, "comment": "A solid performer", "date": "2024-04-06"}]},
    {"brand": "Xiaomi", "model": "13 Ultra", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "90W Fast Charging": True, "120Hz AMOLED": True, "Leica Camera": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "8%"}, "reviews": [{"user": "CameraPhoneFan", "rating": 4.7, "comment": "Great camera system", "date": "2024-04-11"}]},
    {"brand": "Xiaomi", "model": "Redmi Note 12 Pro", "category": "electronics", "features": {"MediaTek Dimensity 1080": True, "67W Fast Charging": True, "120Hz AMOLED": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Medium", "marketShare": "6%"}, "reviews": [{"user": "BudgetMinded", "rating": 4.2, "comment": "Affordable and feature-rich", "date": "2024-04-16"}]},
    {"brand": "Xiaomi", "model": "Redmi K60 Pro", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "120W Fast Charging": True, "120Hz AMOLED": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "4%"}, "reviews": [{"user": "PowerUser", "rating": 4.5, "comment": "Flagship performance at a lower price", "date": "2024-04-21"}]},
    {"brand": "Motorola", "model": "Edge 40 Pro", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "165Hz Display": True, "125W TurboPower Charging": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "8%"}, "reviews": [{"user": "MotoLover", "rating": 4.5, "comment": "Smooth display and fast charging!", "date": "2024-04-15"}]},
    {"brand": "Motorola", "model": "Razr 40 Ultra", "category": "electronics", "features": {"Snapdragon 8+ Gen 1": True, "Foldable Display": True, "External Display": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "Moderate", "marketShare": "5%"}, "reviews": [{"user": "FolderFan", "rating": 4.2, "comment": "Love the foldable design", "date": "2024-05-22"}]},
    {"brand": "Motorola", "model": "Moto G Stylus 5G (2024)", "category": "electronics", "features": {"MediaTek Dimensity 6080": True, "Built-in Stylus": True, "90Hz Display": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "3%"}, "reviews": [{"user": "StylusUser", "rating": 4.0, "comment": "Great value for the stylus", "date": "2024-06-10"}]},
    {"brand": "Motorola", "model": "Moto G Power (2024)", "category": "electronics", "features": {"MediaTek Helio G96": True, "5000mAh Battery": True, "50MP Camera": True}, "insights": {"popularity": "Medium", "priceTrend": "Stable", "demand": "Moderate", "marketShare": "4%"}, "reviews": [{"user": "BatteryKing", "rating": 4.3, "comment": "Amazing battery life", "date": "2024-07-01"}]},
    {"brand": "Motorola", "model": "Moto X40", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "165Hz Display": True, "60MP Camera": True}, "insights": {"popularity": "High", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "7%"}, "reviews": [{"user": "CameraGuru", "rating": 4.7, "comment": "Impressive camera quality", "date": "2024-08-20"}]},
    {"brand": "Nokia", "model": "G60 5G", "category": "electronics", "features": {"Snapdragon 695 5G": True, "120Hz Display": True, "50MP Camera": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "2%"}, "reviews": [{"user": "NokiaFan", "rating": 3.8, "comment": "Good budget 5G phone", "date": "2024-03-05"}]},
    {"brand": "Nokia", "model": "X30 5G", "category": "electronics", "features": {"Snapdragon 695 5G": True, "90Hz AMOLED Display": True, "50MP PureView Camera": True}, "insights": {"popularity": "Low", "priceTrend": "Stable", "demand": "Low", "marketShare": "1%"}, "reviews": [{"user": "CameraLover", "rating": 4.0, "comment": "Decent camera for the price", "date": "2024-04-10"}]},
    {"brand": "Nokia", "model": "XR21", "category": "electronics", "features": {"Snapdragon 695 5G": True, "120Hz Display": True, "Rugged Design": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "1%"}, "reviews": [{"user": "OutdoorEnthusiast", "rating": 4.2, "comment": "Tough and durable phone", "date": "2024-05-15"}]},
    {"brand": "Nokia", "model": "C32", "category": "electronics", "features": {"Unisoc SC9863A1": True, "6.5-inch Display": True, "50MP Camera": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "<1%"}, "reviews": [{"user": "BudgetBuyer", "rating": 3.5, "comment": "Affordable basic phone", "date": "2024-06-20"}]},
    {"brand": "Nokia", "model": "C22", "category": "electronics", "features": {"Unisoc SC9863A": True, "6.5-inch Display": True, "13MP Camera": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "<1%"}, "reviews": [{"user": "BasicUser", "rating": 3.2, "comment": "Simple and cheap", "date": "2024-07-25"}]},
    {"brand": "Sony", "model": "Xperia 1 V", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "4K 120Hz Display": True, "Exmor T for mobile sensor": True}, "insights": {"popularity": "Medium", "priceTrend": "Stable", "demand": "Moderate", "marketShare": "3%"}, "reviews": [{"user": "SonyFanatic", "rating": 4.6, "comment": "Great camera and display", "date": "2024-05-01"}]},
    {"brand": "Sony", "model": "Xperia 5 V", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "120Hz OLED Display": True, "Exmor T for mobile sensor": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "2%"}, "reviews": [{"user": "CompactPhoneUser", "rating": 4.4, "comment": "Powerful compact phone", "date": "2024-06-15"}]},
    {"brand": "Sony", "model": "Xperia 10 V", "category": "electronics", "features": {"Snapdragon 695 5G": True, "OLED Display": True, "Triple Camera System": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "1%"}, "reviews": [{"user": "BudgetConscious", "rating": 4.0, "comment": "Good value mid-ranger", "date": "2024-07-10"}]},
    {"brand": "Sony", "model": "Xperia PRO-I II", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "4K 120Hz HDR OLED display": True, "1-inch image sensor": True}, "insights": {"popularity": "Low", "priceTrend": "Stable", "demand": "Niche", "marketShare": "<1%"}, "reviews": [{"user": "ProPhotographer", "rating": 4.9, "comment": "Amazing camera for professionals", "date": "2024-08-05"}]},
    {"brand": "Sony", "model": "Xperia 10 IV", "category": "electronics", "features": {"Snapdragon 695 5G": True, "OLED Display": True, "Triple Camera System": True}, "insights": {"popularity": "Low", "priceTrend": "Decreasing", "demand": "Low", "marketShare": "1%"}, "reviews": [{"user": "ValueSeeker", "rating": 3.8, "comment": "Decent phone for the price", "date": "2024-09-01"}]},
    {"brand": "Asus", "model": "ROG Phone 7 Ultimate", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "165Hz AMOLED Display": True, "AeroActive Cooler 7": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "6%"}, "reviews": [{"user": "GamerPro", "rating": 4.8, "comment": "Ultimate gaming phone", "date": "2024-04-20"}]},
    {"brand": "Asus", "model": "Zenfone 10", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "144Hz AMOLED Display": True, "Gimbal Stabilization 2.0": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "4%"}, "reviews": [{"user": "TechEnthusiast", "rating": 4.5, "comment": "Great performance and camera", "date": "2024-05-25"}]},
    {"brand": "Asus", "model": "ROG Phone 7", "category": "electronics", "features": {"Snapdragon 8 Gen 2": True, "165Hz AMOLED Display": True, "AirTrigger 6": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "5%"}, "reviews": [{"user": "MobileGamer", "rating": 4.7, "comment": "Excellent gaming experience", "date": "2024-06-25"}]},
    {"brand": "Asus", "model": "Zenfone 9", "category": "electronics", "features": {"Snapdragon 8+ Gen 1": True, "120Hz AMOLED Display": True, "Gimbal Stabilization": True}, "insights": {"popularity": "Medium", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "3%"}, "reviews": [{"user": "CompactPhoneLover", "rating": 4.3, "comment": "Powerful and compact", "date": "2024-07-30"}]},
    {"brand": "Asus", "model": "ROG Phone 6D Ultimate", "category": "electronics", "features": {"MediaTek Dimensity 9000+": True, "165Hz AMOLED Display": True, "AeroActive Portal": True}, "insights": {"popularity": "High", "priceTrend": "Decreasing", "demand": "Moderate", "marketShare": "4%"}, "reviews": [{"user": "HardcoreGamer", "rating": 4.6, "comment": "Great performance for gaming", "date": "2024-08-30"}]}
]

# Function to generate embeddings for dietary preferences
def generate_embeddings(text):
    aiplatform.init(project=PROJECT_ID, location=REGION)
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
    return embedding_model.get_embeddings([text])[0].values

# Initialize Pinecone
try:
    pc = Pinecone(api_key='pcsk_6XfUhD_URrTDuNDagfChu6YHGvqnxHCK9ajrBM9yNbX3Rp6ZNYoxdV5h9oLDXTdnCarF8i')
    logger.info("Successfully initialized Pinecone")
except Exception as e:
    logger.error("Failed to initialize Pinecone: %s", e)
    raise

# Create a Pinecone index with the correct dimension
index_name = 'product-index'
dimension = 1024

# Connect to the index
try:
    index = pc.Index(index_name)
    logger.info("Successfully connected to Pinecone index")
except Exception as e:
    logger.error("Failed to connect to Pinecone index: %s", e)
    raise

# Store recipe data in the index
try:
    for product in products:
        combined_text = f"Brand: {product['brand']}, Model: {product['model']}, Category: {product['category']}, Features: {product['features']}, Insights: {product['insights']}, Reviews: {product['reviews']}"
        embedding = generate_embeddings(combined_text)
        index.upsert(vectors=[
            (product["model"], embedding, {
                "brand": product["brand"],
                "model": product["model"],
                "category": product["category"],
                "features": str(product["features"]),
                "insights": str(product["insights"]),
                "reviews": str(product["reviews"])
            })
        ])
    logger.info("Successfully uploaded data to Pinecone index")
except Exception as e:
    logger.error("Failed to upload data to Pinecone index: %s", e)
    raise


