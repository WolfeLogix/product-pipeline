# from dotenv import load_dotenv
import os

from shopify_util import shopify_util

# # Load environment variables from .env file
# load_dotenv('.env')

if __name__ == "__main__":
    store = shopify_util()
    status = store.create_product()
    print(status)