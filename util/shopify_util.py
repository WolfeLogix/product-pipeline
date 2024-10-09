from os import getenv
import uuid
import random
import time

import shopify  # https://github.com/Shopify/shopify_python_api

current_time = int(time.time())
random.seed(current_time)


class ShopifyUtil():
    """This class sets up the shopify API connection."""
    
    def __init__(self):
        """This method intitializes the variables required for the connection."""
        SHOP_NAME = getenv('SHOPIFY_SHOP_NAME')
        API_KEY = getenv('SHOPIFY_API_KEY')
        API_SECRET = getenv('SHOPIFY_API_SECRET')
        SHOP_URL = f"https://{API_KEY}:{API_SECRET}@{SHOP_NAME}.myshopify.com/admin"

        shopify.ShopifyResource.set_site(SHOP_URL)
        self.shop = shopify.Shop.current

    def get_products(self, product_id):
        """This method retrieves all products from the shopify store."""
        product = shopify.Product.find(product_id)
        return product
        
    def create_product(self):
        """This method creates a new product in the shopify store."""
        
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


