import requests
from os import getenv
import uuid
import random
import time

current_time = int(time.time())
random.seed(current_time)

class printify_util():
    """
    This class sets up the Printify API connection.
    Documentation: https://developers.printify.com/
    Store Login: https://printify.com/app/dashboard
    Printify Rate Limit is 600 requests per minute, returns 429 if exceeded.
    """
    
    def __init__(self):
        """This method initializes the variables required for the connection."""
        self.API_KEY = getenv('PRINTIFY_API_KEY')
        self.BASE_URL = "https://api.printify.com/v1"
        self.store_id = None
        self.headers = {
            'Authorization': f'Bearer {self.API_KEY}'
        }
        self.fetch_store_id()

    def fetch_store_id(self):
        """Fetches the store ID from the Printify API and stores it in self.store_id."""
        url = f"{self.BASE_URL}/shops.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Collect the first available store ID
                self.store_id = data[0]['id']
                print(f"Store ID: {self.store_id}")
            else:
                print("No stores found in the response.")
        else:
            print(f"Failed to fetch stores. Status code: {response.status_code}")

    def get_product_catalog(self):
        """Fetches and prints the product catalog from the Printify API."""
        url = f"{self.BASE_URL}/catalog/products.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print(data)
            #TODO - Write this to a file
        else:
            print(f"Failed to fetch product catalog. Status code: {response.status_code}")

    def get_all_variants(self, product_id, print_provider_id):
        """Given a product ID and print provider id get all unique variants per print provider"""
        # get all variants for each print provider and return a list dictionaries that include id, color, size, and for each placeholder with position front a height and width
        # https://api.printify.com/v1/catalog/blueprints/{{blueprint_id}}/print_providers/{{print_provider_id}}/variants.json
        url = f"{self.BASE_URL}/catalog/blueprints/{product_id}/print_providers/{print_provider_id}/variants.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch product catalog. Status code: {response.status_code}")

        # Parse response
        return_response = []
        unique_print_sizes = []
        
        for variant in response.json()['variants']:
            for placeholder in variant['placeholders']:
                return_response.append({
                    'id': variant['id'],
                    'color': variant['options']['color'],
                    'size': variant['options']['size'],
                    'placeholder': placeholder
                })
                if placeholder not in unique_print_sizes:
                    unique_print_sizes.append(placeholder)
        print(len(return_response))
        return return_response

        
