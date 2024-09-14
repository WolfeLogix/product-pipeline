from os import getenv
import shopify


class shopify_util():
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
        new_product = shopify.Product()
        new_product.title = "Burton Custom Freestyle 151"
        new_product.product_type = "Snowboard"
        new_product.vendor = "Burton"
        success = new_product.save() 
        return success


