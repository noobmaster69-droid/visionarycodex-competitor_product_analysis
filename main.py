from dotenv import load_dotenv
from agents.serpapi_agent import SerpAPIAgent
from agents.amazon_review_agent import AmazonReviewAgent
from agents.analysis_agent import AnalysisAgent
from agents.visualization_agent import VisualizationAgent
from agents.monitoring_agent import MonitoringAgent
from services.embedding_service import EmbeddingService
from services.matching_engine_service import MatchingEngineService
formal-loop-452705-h1
PROJECT_ID = "ai-cons-ma-cpa01"
LOCATION = "asia-south1"
SERPAPI_API_KEY = "8c2d7fbdcf711b048994c14ded601a5caeab1a996b4778f3ddb4f8dbaea5f20c"
PRODUCT_INDEX_NAME = "product-index"
REVIEW_INDEX_NAME = "review-index"

def main(product_category, competitors):
    """Main function to analyze a product."""

    # logger.info(f"Analyzing product: {product_category}, Competitors: {competitors}")

    serpapi_agent = SerpAPIAgent(SERPAPI_API_KEY)

    amazon_agent = AmazonReviewAgent()

    analysis_agent = AnalysisAgent()

    visualization_agent = VisualizationAgent()

    monitoring_agent = MonitoringAgent()

    embedding_service = EmbeddingService()

    matching_service = MatchingEngineService(PROJECT_ID, LOCATION, PRODUCT_INDEX_NAME, REVIEW_INDEX_NAME)

    product_query = f"{product_category} {competitors_input}"

    google_data = serpapi_agent.get_google_shopping_data(product_query)

    if not google_data:
        # logger.warning("No Google Shopping data found.")

        return "No Google Shopping data found for the given query."

    product_ids = [item.get("product_id") for item in google_data if item.get("product_id")]

    product_titles = [item.get("title") for item in google_data if item.get("title")]

    product_embeddings = embedding_service.create_embeddings(product_titles)

    matching_service.store_embeddings(PRODUCT_INDEX_NAME, product_ids, product_embeddings,
                                      [{"type": "product"} for _ in product_ids])

    if product_ids:

        amazon_reviews = amazon_agent.get_amazon_reviews(product_ids[0])

        review_embeddings = embedding_service.create_embeddings(amazon_reviews)

        review_ids = [f"review_{i}" for i in range(len(amazon_reviews))]

        matching_service.store_embeddings(REVIEW_INDEX_NAME, review_ids, review_embeddings,
                                          [{"type": "review"} for _ in review_ids])

        similar_products = matching_service.search_similar_items(PRODUCT_INDEX_NAME, product_embeddings[0])

        similar_reviews = matching_service.search_similar_items(REVIEW_INDEX_NAME, review_embeddings[0])

        analysis_report = analysis_agent.generate_analysis_report(product_titles[0], amazon_reviews, similar_products,
                                                                  similar_reviews)

        visualizations = visualization_agent.generate_visualizations(analysis_report)

        # Simulate log collection

        logs = [

            open("logs/main.log").read(),

            open("logs/serpapi_agent.log").read(),

            open("logs/amazon_review_agent.log").read(),

            open("logs/embedding_service.log").read(),

            open("logs/matching_engine_service.log").read(),

            open("logs/analysis_agent.log").read(),

            open("logs/visualization_agent.log").read()

        ]

        log_analysis = monitoring_agent.analyze_logs(logs)

        return {

            "analysis_report": analysis_report,

            "visualizations": visualizations,

            "log_analysis": log_analysis

        }

    else:


        return "No product IDs found in Google Shopping data."

    # --- Example Usage ---

if __name__ == "__main__":
    product_category = input("Please enter a product category: ")
    competitors_input = input("Please enter competitors (comma-separated): ")
    competitors = competitors_input.split(',')

    results = main(product_category, competitors)
    print(results)
