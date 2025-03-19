import random
# from utils.logger import setup_logger
# logger = setup_logger('amazon_review_agent', 'logs/amazon_review_agent.log')

class AmazonReviewAgent:
    def get_amazon_reviews(self, product_id):
        """Simplified example: Fetches reviews (replace with actual scraping/API)."""
        # logger.info(f"Fetching Amazon reviews for product ID: {product_id}")
        reviews = [
            f"Review {i} for product {product_id}. This is a great product!",
            f"Review {i + 1} for product {product_id}. I'm very satisfied.",
            f"Review {i + 2} for product {product_id}. It's okay, but could be better.",
            f"Review {i + 3} for product {product_id}. Not what I expected.",
            f"Review {i + 4} for product {product_id}. Excellent quality!"
        ]
        random.shuffle(reviews)
        return reviews[:3]