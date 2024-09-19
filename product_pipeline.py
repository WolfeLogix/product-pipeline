# from dotenv import load_dotenv
import os

from shopify_util import shopify_util
from printify_util import printify_util

# # Load environment variables from .env file
# load_dotenv('.env')

if __name__ == "__main__":
    """Printify Add Product"""

    ### for item spreadsheet:

    # Initialize Shopify and Printify API connections
    printify = printify_util()

    # Manually Select Blueprint (6 = Unisex Gildan T-Shirt)
    BLUEPRINT_ID = 6

    # Query to get a list of print providers for the blueprint
    providers = printify.get_all_providers(BLUEPRINT_ID)
    PRINT_PROVIDER_ID = 110

    # Query to get a list of variants for the blueprint
    variants = printify.get_all_variants(BLUEPRINT_ID, PRINT_PROVIDER_ID)

    # Query to get a list of shipping costs for each variant
    shipping_cost = printify.get_shipping_costs(BLUEPRINT_ID, PRINT_PROVIDER_ID)

    # # Upload Images to Printify / Github
    # image_url = "https://raw.githubusercontent.com/parishwolfe/product-pipeline/refs/heads/main/HelloWorld_white.png"
    # printify.upload_image(image_url)

    # Create Product in Printify
    printify.create_product(
        blueprint_id=BLUEPRINT_ID, 
        print_provider_id=PRINT_PROVIDER_ID, 
        variants=variants, 
        image_id="66eb5eb5557b6ed02c9276aa"
    )

    # Publish Product in Printify (Rate Limited to 200/30min or 1 per 10 seconds)
    # TODO - printify.publish_product(PRODUCT_ID)