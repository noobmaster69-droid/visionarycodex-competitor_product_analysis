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
    {"brand": "Samsung", "model": "Galaxy S24+", "category": "electronics", "features": {"Snapdragon 8 Gen 3 for Galaxy": True, "Dynamic AMOLED 2X": True, "Enhanced Telephoto Lens": True}, "insights": {"popularity": "High", "priceTrend": "Stable", "demand": "High", "marketShare": "18%"}, "reviews": [{"user": "TechEnthusiast", "rating": 4.6, "comment": "Great all-around phone", "date": "2024-03-05"}]}
]

myProducts = [
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX1 Chip': True, 'FlexOLED Display': True, 'Dual Matrix Camera': True}",
      "insights":
        "{'popularity': 'High', 'priceTrend': 'Rising', 'demand': 'High', 'marketShare': '18%'}",
      "model": "X-Fold Pro",
      "reviews":
        "[{'user': 'TechEarly', 'rating': 4.2, 'comment': 'Innovative folding phone', 'date': '2024-04-15'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX2 Chip': True, '4K HDR Display': True, '100W Fast Charging': True}",
      "insights":
        "{'popularity': 'Very High', 'priceTrend': 'Stable', 'demand': 'Extreme', 'marketShare': '25%'}",
      "model": "Prime 2024",
      "reviews":
        "[{'user': 'PowerUser', 'rating': 4.9, 'comment': 'Best flagship phone', 'date': '2024-03-28'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Lite Chip': True, 'AMOLED Display': True, '48MP Camera': True}",
      "insights":
        "{'popularity': 'Medium', 'priceTrend': 'Decreasing', 'demand': 'Medium', 'marketShare': '12%'}",
      "model": "Nova Lite",
      "reviews":
        "[{'user': 'BudgetBuyer', 'rating': 4.3, 'comment': 'Great mid-range option', 'date': '2024-04-01'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Pro Chip': True, '6.8\" Curved Display': True, '200MP Camera': True}",
      "insights":
        "{'popularity': 'High', 'priceTrend': 'Stable', 'demand': 'High', 'marketShare': '15%'}",
      "model": "Nova Ultra",
      "reviews":
        "[{'user': 'PhotoPro', 'rating': 4.7, 'comment': 'Camera beast!', 'date': '2024-03-22'}]",
    },
    {
      "brand": "TechNova",
      "category": "electronics",
      "features":
        "{'NovaX Gaming Chip': True, '144Hz Display': True, 'Active Cooling': True}",
      "insights":
        "{'popularity': 'Medium', 'priceTrend': 'Stable', 'demand': 'Medium', 'marketShare': '8%'}",
      "model": "Nova Play",
      "reviews":
        "[{'user': 'MobileGamer', 'rating': 4.5, 'comment': 'Smooth gaming experience', 'date': '2024-04-05'}]",
    },
  ]

# Function to generate embeddings for dietary preferences
def generate_embeddings(text):
    aiplatform.init(project=PROJECT_ID, location=REGION)
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
    return embedding_model.get_embeddings([text])[0].values


def upsert_data_new(data):
    # Initialize Pinecone
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        logger.info("Successfully initialized Pinecone")
    except Exception as e:
        logger.error("Failed to initialize Pinecone: %s", e)
        raise

    # Connect to the index
    index_name = INDEX_NAME
    try:
        index = pc.Index(index_name)
        logger.info("Successfully connected to Pinecone index")
    except Exception as e:
        logger.error("Failed to connect to Pinecone index: %s", e)
        raise

    try:
        combined_text = f"Brand: {data['competitorName']}, Model: {data['model']}, Details: {data['details']}, Features: {data['features']}, Insights: {data['insights']}, Reviews: {data['reviews']}"
        embedding = generate_embeddings(combined_text)
        index.upsert(vectors=[
            (data["model"], embedding, {
                "brand": data["competitorName"],
                "model": data["model"],
                "details": str(data["details"]),
                "features": str(data["features"]),
                "insights": str(data["insights"]),
                "reviews": str(data["reviews"])
            })
        ])
        logger.info("Successfully uploaded data to Pinecone index")
    except Exception as e:
        logger.error("Failed to upload data to Pinecone index: %s", e)
        raise



def upsert_data(products):
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

    try:
        combined_text = f"Brand: {products['brand']}, Model: {products['model']}, Category: {products['category']}, Features: {products['features']}, Insights: {products['insights']}, Reviews: {products['reviews']}"
        embedding = generate_embeddings(combined_text)
        index.upsert(vectors=[
            (products["model"], embedding, {
                "brand": products["brand"],
                "model": products["model"],
                "category": products["category"],
                "features": str(products["features"]),
                "insights": str(products["insights"]),
                "reviews": str(products["reviews"])
            })
        ])

        data = {
                "competitorName": "Asus",
                "model": "Rog Phone",
                "details": {
                    "featureImportance": {
                        "price": 0.4,
                        "specialFeatures": 0.3,
                        "userRating": 0.3
                    },
                    "numberOfReviews": "708",
                    "price": ["$999.99", "$999.99", "$999.99"],
                    "reviewSentiment": {
                        "negative": "8.47457627118644%",
                        "neutral": "4.23728813559322%",
                        "positive": "87.28813559322035%"
                    },
                    "specialFeatures": [
                        "DISPLAY 6.78 inches",
                        "PROCESSOR Qualcomm SM8750-AB Snapdragon 8 Elite (3 nm)",
                        "FRONT CAMERA 32MP",
                        "REAR CAMERA 50MP+13MP+5MP",
                        "BATTERY CAPACITY 5800 mAh, non-removable"
                    ],
                    "userRating": "4.4"
                },
                "features": {
                    "assistant": "Google Assistant",
                    "battery": "5800 mAh",
                    "bluetooth": "5.4, A2DP, LE, aptX HD, aptX Adaptive, aptX Lossless",
                    "chip": "Qualcomm SM8750-AB Snapdragon 8 Elite (3 nm)",
                    "display": "1080 x 2400 pixels, 20:9 ratio (~388 ppi density)",
                    "dualSim": True,
                    "gps": True,
                    "nfc": True,
                    "protection": "Corning Gorilla Glass Victus 2",
                    "security": "Fingerprint",
                    "thumbnail": "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcRYT0b--DHdL6oVLePPnNKdVPHwqsX6mPRLfqD6rbW3ahZefcIJKAUmDtBtgcYSpB4KvE1VNkKPuBwyxWmcItZLrqRKo8l9pQ&usqp=CAY",
                    "waterResistance": "IP68",
                    "weight": "227 g (8.01 oz)",
                    "wifi": "Wi-Fi 802.11 a/b/g/n/ac/6e/7, tri-band, Wi-Fi Direct",
                    "wirelessCharging": "15W wireless"
                },
                "insights": {
                    "Availability": "Available at Amazon.com - Seller, Target, Newegg.com - Mobile Advance, and Mobile Advance",
                    "demand": "High",
                    "popularity": "High",
                    "priceTrend": "Neutral"
                },
                "isMyCompanyProduct": False,
                "reviews": [
                    {
                        "comment": "As described! I had ordered a red magic at first because it was slightly cheaper and and a sleeker design. However when I did get it it was not compatible with us cell towers!! I couldn't activate it with any carrier I was pleasantly surprised that the rog9 pro is compatible with all US carriers!!!! This is the reason I switched!!! And I love this phone it replaced my laptop because it's way more powerful and has a touchscreen thank you for a quality purchase!!",
                        "date": "Reviewed in the United States on March 1, 2025",
                        "rating": 5,
                        "user": "dean8859"
                    },
                    {
                        "comment": "I recently purchased this phone. It is expensive but not worth it. Constantly having issues and the connectivity is really bad. Also the speed is very slow. Poorly done",
                        "date": "Reviewed in the United States on February 25, 2025",
                        "rating": 1,
                        "user": "Sena SARIYER"
                    },
                    {
                        "comment": "Love it amazing awesome phone can't believe it came very easy to operate",
                        "date": "Reviewed in the United States on March 8, 2025",
                        "rating": 5,
                        "user": "cool bag "
                    },
                    {
                        "comment": "Great phone.Great features. Fun.Touch screen died after 4 days, basically just after getting the device tailored to my needs.Bummer...",
                        "date": "Reviewed in the United States on February 2, 2025",
                        "rating": 3,
                        "user": "UCF Knightman"
                    },
                    {
                        "comment": "Previously owned a Samsung Z Fold3 and daily-drove mostly Samsung smartphones.The performance is obserdly good. Samsung's folding phones get the same chip in ROG phones, but like half a year, or more later every time.The back LED display is a nice attention-grabbing gimmick, but if you ever want a kickstand that isn't Asus' chonky ROG cooler attachment, or if you want compatibility with MagSafe, or magnetic accessories, you'll probably end up with a case that obstructs part, or all of the rear LED area.I'm able to play Genshin Impact with maxed settings just fine without the cooler attachment. There is some slight heat buildup without the cooler, but nothing major. The time it takes to safely attach the cooler without damaging the phone, or the cooler's USB C connection is quite inconvenient. The cooler sits in it's pouch at home, until the day when I plan to stay the night anywhere but home and forget to bring my Nintendo Switch. Mobile games are pathetic, although there is Genshin Impact and a mobile version of Final Fantasy XIV was recently announced to be in the works.Things I severely miss from my Samsung phones that the Google Playstore has no equal:1. Samsung Notes.2. A single, do-it-all gallery app that isn't a mess of your pictures and albums thrown to the wind (Google has like 3 different apps and they're all horrible in many ways. I have them all installed and have to keep jumping around between them for different reasons.3. Secure Folder.4. Splitting the screen between 2 apps was a lot quicker on Samsung. You could even create your own shortcuts for the home screen and even the sidebar menu to launch paired apps instantly.5. You could set videos as Live Wallpapers straight from the gallery, without the need of the Wallpaper Engine app.6. The ROG Phone 9 instantly refused to work properly with my Samsung Galaxy 3 Frontier smart watch (yes the Galaxy Wear app was utilized), making me watch-less at the moment. I use voice-dictation for text messaging from my watch heavily throughout every workday and no-longer have that capability.7. Bixby was far from being Alexa, or Siri, but it was still far better then Google Assistant and Gemini. So many simple commands, yet not smart enough to comply.I missed out on the previous gen ROG phones, with their stronger gamer aesthetics. Things are going in the wrong direction.The 65W Hyper Charging is amazing and so is the battery life.I don't need the absolute best camera, but I do need that's current and this suffices.Went down from a 1440p experience to a 1080p. Despite this I'm not noticing the pixels and am still content. The brightness is a bit weak though. Compared to Samsung, I find myself cranking the brightness to 100% outdoors and 50-75% for GPS in the car during the day vs 40% on my old Samsung Z Fold3.If Conclusion:If you want the aesthetics, battery-life, wired charging speed & performance, that's all you'll be getting. Everything else will be a headache. I love Asus ROG products and would like to see better coming from them, so they don't die out like the Razer Phone, or LG. They need to put the focus on the software and stop relying on Google and small app store developers to fill in the gaps, because they're not doing a good job of it. I'll be sticking with this phone for the next 2-4 years as I typically tend to do. If there are no improvements during that time to solve at least half of the issues I've listed, then I'm sure I'd be going back to Samsung. Apple is not an option for me. I've owned an iPhone and don't like the restrictions and pay-walls blocking what would be otherwise easy, free and/or more customizable on Android.",
                        "date": "Reviewed in the United States on February 24, 2025",
                        "rating": 4,
                        "user": "Fred B."
                    },
                    {
                        "comment": "The anime play on the screen off option is limited to preloaded default rog signatures only, no custom signature option are open to screen off",
                        "date": "Reviewed in the United States on February 5, 2025",
                        "rating": 1,
                        "user": "Kevin"
                    }
                ]
            }
        logger.info("Successfully uploaded data to Pinecone index")
    except Exception as e:
        logger.error("Failed to upload data to Pinecone index: %s", e)
        raise