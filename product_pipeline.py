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
    VARIANT_ID = 12124

    # Query to get a list of shipping costs for each variant
    shipping_cost = printify.get_shipping_costs(BLUEPRINT_ID, PRINT_PROVIDER_ID)


    # Upload Images to Printify / Github
    # TODO - printify.upload_images(BLUEPRINT_ID, PRINT_PROVIDER_ID, variants)
    # OR
    # TODO - github commit images to public repo

    # Create Product in Printify
    # TODO - printify.create_product(BLUEPRINT_ID, PRINT_PROVIDER_ID, variants, shipping_costs, image)

    # Publish Product in Printify (Rate Limited to 200/30min or 1 per 10 seconds)
    # TODO - printify.publish_product(PRODUCT_ID)