"""This is a utility class for listing and creating products in Printify."""
from os import getenv
import random
import time

import requests

current_time = int(time.time())
random.seed(current_time)


class PrintifyUtil():
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
        self.typical_size_price = 2399
        self.extended_size_price = 2999

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
            print(f"Failed to fetch stores. Status code: {
                  response.status_code}")

    def get_product_catalog(self):
        """Fetches and prints the product catalog from the Printify API."""
        url = f"{self.BASE_URL}/catalog/products.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            print("Successully fetched product catalog")
            # with open("catalog.json", "wb") as file:
            #     file.write(response.text.encode('utf-8'))
        else:
            print(f"Failed to fetch product catalog. Status code: {
                  response.status_code}")

    def get_all_providers(self, blueprint_id):
        """Given a blueprint_id, get all print providers for that blueprint."""
        uri = f"{
            self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers.json"
        response = requests.get(uri, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch print providers. Status code: {
                  response.status_code}")
        print("Successully fetched print providers")
        # Parse response
        provider_ids = []
        for provider in response.json():
            provider_ids.append(provider['id'])
        return provider_ids

    def get_all_variants(self, blueprint_id, print_provider_id):
        """Given a product ID and print provider id get all unique variants per print provider"""
        # get all variants for each print provider and return a list dictionaries that include id, color, size, and for each placeholder with position front a height and width
        # https://api.printify.com/v1/catalog/blueprints/{{blueprint_id}}/print_providers/{{print_provider_id}}/variants.json
        url = f"{self.BASE_URL}/catalog/blueprints/{
            blueprint_id}/print_providers/{print_provider_id}/variants.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch product catalog. Status code: {
                  response.status_code}")
        print("Successully fetched variants")
        # Parse response
        return_response = []
        unique_print_sizes = []
        default_variant_set = False

        for variant in response.json()['variants']:
            # TODO - Remove this nested loop
            for placeholder in variant['placeholders']:
                price = None
                default_variant = False
                match variant['options']['size']:
                    case "XS":
                        price = self.typical_size_price
                    case "S":
                        price = self.typical_size_price
                    case "M":
                        price = self.typical_size_price
                    case "L":
                        price = self.typical_size_price
                        if variant['options']['color'] == "Black" and not default_variant_set:
                            default_variant = True
                            default_variant_set = True
                    case "XL":
                        price = self.typical_size_price
                    case _:
                        price = self.extended_size_price
                        continue
                if variant['options']['color'] not in [
                    "Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Orange", "purple"
                ]:
                    continue
                return_response.append({
                    'id': variant['id'],
                    # 'color': variant['options']['color'],
                    # 'size': variant['options']['size'],
                    # 'placeholder': placeholder
                    "price": price,
                    "is_enabled": True,
                    "is_default": default_variant
                })
                if placeholder not in unique_print_sizes:
                    unique_print_sizes.append(placeholder)
        return return_response

    def get_shipping_costs(self, blueprint_id, print_provider_id):
        """Given a product ID, print provider id, and variants, get USA shipping costs for each variant"""
        url = f"{self.BASE_URL}/catalog/blueprints/{
            blueprint_id}/print_providers/{print_provider_id}/shipping.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch shipping costs. Status code: {
                  response.status_code}")

        # Parse response
        for shipping_cost in response.json().get("profiles"):
            if "US" in shipping_cost.get("countries"):
                cost = shipping_cost.get("first_item").get("cost")
                return cost
        return None

    def upload_image(self, image_url: str):
        """Uploads an image to Printify and returns the URL."""
        url = f"{self.BASE_URL}/uploads/images.json"
        file_name = image_url.split("/")[-1]
        data = {
            "file_name": file_name,
            "url": image_url
        }
        response = requests.post(url, headers=self.headers, json=data)
        print(response.status_code)
        print(response.json())
        if response.status_code == 200:
            print(f"Image uploaded successfully: {file_name}")
            print(response.json()['id'])
            return response.json()['id']
        else:
            print(f"Failed to upload image. Status code: {
                  response.status_code}")
            return None
        # {'id': '66eb5eb5557b6ed02c9276aa', 'file_name': 'HelloWorld_white.png', 'height': 3700, 'width': 3300, 'size': 32789, 'mime_type': 'image/png', 'preview_url': 'https://pfy-prod-image-storage.s3.us-east-2.amazonaws.com/19824847/8d1780de-bc40-49b2-bb05-8eb1908aa214', 'upload_time': '2024-09-18 23:13:57'}

    def create_product(
            self,
            blueprint_id,
            print_provider_id,
            variants,
            image_id,
            title,
            description,
            marketing_tags
    ):
        """Creates a product in Printify."""
        url = f"{self.BASE_URL}/shops/{self.store_id}/products.json"
        product = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "tags": marketing_tags,
            # [{"id": 123, "price": 1999, is_enabled: true}]
            "variants": variants,
            "print_areas": [
                {
                    "variant_ids": [variant['id'] for variant in variants],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": image_id,
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1,
                                    "angle": 0
                                }
                            ]

                        }
                    ]
                }
            ]
        }
        response = requests.post(url, headers=self.headers, json=product)
        if response.status_code == 200:
            print(f"Product created successfully: {response.json()['id']}")
            return response.json()['id']
            # # write response to a file
            # with open("product.json", "wb") as file:
            #     file.write(response.text.encode('utf-8'))

        else:
            print(f"Failed to create product. Status code: {
                  response.status_code}")
            return None

    def publish_product(self, product_id):
        """Publishes a product in Printify."""
        url = f"{
            self.BASE_URL}/shops/{self.store_id}/products/{product_id}/publish.json"
        data = {
            "title": True,
            "description": True,
            "images": True,
            "variants": True,
            "tags": True
            # "keyFeatures": True,
            # "shipping_template": True
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Product published successfully: {product_id}")
            print(response.json())
        else:
            print(f"Failed to publish product. Status code: {
                  response.status_code}")

        # TODO - update product with correct prices after shipping cost and cogs
