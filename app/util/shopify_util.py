from os import getenv
import uuid
import random
import time

import shopify  # https://github.com/Shopify/shopify_python_api

current_time = int(time.time())
random.seed(current_time)


class ShopifyUtil():
    """This class sets up the Shopify API connection."""

    def __init__(self):
        """This method initializes the variables required for the connection."""
        SHOP_NAME = getenv('SHOPIFY_SHOP_NAME')
        API_KEY = getenv('SHOPIFY_API_KEY')
        API_SECRET = getenv('SHOPIFY_API_SECRET')
        SHOP_URL = f"https://{API_KEY}:{API_SECRET}@{SHOP_NAME}.myshopify.com/admin"

        if not all([SHOP_NAME, API_KEY, API_SECRET]):
            raise ValueError(
                "Missing one or more required environment variables.")

        shopify.ShopifyResource.set_site(SHOP_URL)
        self.shop = shopify.Shop.current

    def healthcheck(self):
        """Check the health of the Shopify API connection."""
        try:
            self.shop = shopify.Shop.current()
            print("API connection successful.")
            return "OK"
        except Exception as e:
            print(f"API connection failed: {e}")
            return "ERROR"
        finally:
            shopify.ShopifyResource.clear_session()

    def get_products(self, product_id):
        """This method retrieves all products from the Shopify store."""
        product = shopify.Product.find(product_id)
        return product

    def create_product(self):
        """This method creates a new product in the Shopify store."""

        # Basic product information
        new_product = shopify.Product()
        new_product.title = "Short Sleeve T-Shirt 7"
        new_product.product_type = "T-Shirt"
        new_product.vendor = "Printful"
        # Description is the `body_html` field in Shopify
        new_product.body_html = "Expertly crafted with 100&#37; cotton, this t-shirt offers unbeatable comfort and breathability. Perfect for everyday wear, its durable design ensures long-lasting quality. Elevate your wardrobe with this versatile and essential piece."
        new_product.tags = "t-shirt, short sleeve, cotton, printful"

        # Define product variants
        colors = ['Black', 'White', 'Blue']
        sizes = ['Small', 'Medium', 'Large']
        variants = []

        # Add required fields for each variant
        for color in colors:
            for size in sizes:
                variant = shopify.Variant()
                variant.option1 = color
                variant.option2 = size
                variant.price = '25.99'
                variant.sku = str(uuid.UUID(int=random.getrandbits(128)))
                variants.append(variant)

        # Set the product options
        new_product.options = [
            {"name": "Color", "values": colors},
            {"name": "Size", "values": sizes}
        ]

        # Assign variants to the product
        new_product.variants = variants

        # Upload product images
        image_path = "./T-Shirt-Black-PNG.png"
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image = shopify.Image()
            image.attach_image(image_data, filename=image_path.split('/')[-1])
            new_product.images = [image]

        # Save the product
        success = new_product.save()
        if not success:
            print("Error saving product:", new_product.errors.full_messages())
        return success

    def update_all_products_to_category(self, category_id):
        """This method updates all products to a specific product category."""
        page = 1
        products_per_page = 250

        while True:
            products = shopify.Product.find(limit=products_per_page, page=page)
            if not products:
                break

            for product in products:
                product.product_category = {
                    "product_taxonomy_node_id": category_id}
                if product.save():
                    print(f"Updated product ID {
                          product.id} to category ID {category_id}")
                else:
                    print(f"Failed to update product ID {
                          product.id}", product.errors.full_messages())

            page += 1

    def fetch_product_taxonomy_node_id(self, category_name):
        """Fetches the taxonomy node ID for a given category name."""
        taxonomy_nodes = shopify.ProductTaxonomyNode.find()
        for node in taxonomy_nodes:
            if node.name.lower() == category_name.lower():
                return node.id
        print(f"Category {category_name} not found in taxonomy.")
        return None