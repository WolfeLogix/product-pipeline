"""This is a utility class for listing and creating products in Printify."""
from os import getenv
import random
import time

import requests
from ratelimit import limits, sleep_and_retry

current_time = int(time.time())
random.seed(current_time)

# Prinitify Rate Limits
PRINTIFY_RATE_LIMIT = 600
PRINTIFY_RATE_PERIOD = 60  # 1 minute
PUBLISH_RATE_LIMIT = 200
PUBLISH_RATE_PERIOD = 1800  # 30 minutes


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

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
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
                return self.store_id
            else:
                print("No stores found in the response.")
        else:
            print(f"Failed to fetch stores. Status code: {
                  response.status_code}")

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def get_product_catalog(self):
        """Fetches and prints the product catalog from the Printify API."""
        url = f"{self.BASE_URL}/catalog/products.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            print("Successfully fetched product catalog")
        else:
            print(f"Failed to fetch product catalog. Status code: {
                  response.status_code}")

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def get_all_providers(self, blueprint_id):
        """Given a blueprint_id, get all print providers for that blueprint."""
        uri = f"{
            self.BASE_URL}/catalog/blueprints/{blueprint_id}/print_providers.json"
        response = requests.get(uri, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch print providers. Status code: {
                  response.status_code}")
        print("Successfully fetched print providers")
        provider_ids = []
        for provider in response.json():
            provider_ids.append(provider['id'])
        return provider_ids

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def get_all_variants(self, blueprint_id, print_provider_id):
        """Given a product ID and print provider id get all unique variants per print provider"""
        url = f"{self.BASE_URL}/catalog/blueprints/{
            blueprint_id}/print_providers/{print_provider_id}/variants.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch product catalog. Status code: {
                  response.status_code}")
        print("Successfully fetched variants")
        return_response = []
        default_variant_set = False
        light_variant_ids = []
        dark_variant_ids = []
        supported_colors = [
            "Black",
            "White",
            "Cardinal Red",
            "Carolina Blue",
            "Sport Grey",
            "Red",
            "Light Pink",
            "Navy",
            "Sapphire",
            "Sunset",
            "Turf Green",
            "Military Green",
            "Heliconia",
            "Charcoal",
            "Purple",
            "Heather Sapphire"
        ]
        # Set a default color for the product
        default_color = random.choice(supported_colors)

        for variant in response.json()['variants']:
            price = None
            default_variant = False
            available = True
            variant_count = 0

            # Don't allow colors that are outside of the supported colors
            if variant['options']['color'] not in supported_colors:
                continue

            # Don't allow certain sizes outside of the supported sizes
            match variant['options']['size']:
                case "XS":
                    price = self.typical_size_price
                case "S":
                    price = self.typical_size_price
                case "M":
                    price = self.typical_size_price
                case "L":
                    price = self.typical_size_price
                    if variant['options']['color'] == default_color and not default_variant_set:
                        default_variant = True
                        default_variant_set = True
                case "XL":
                    price = self.typical_size_price
                case "2XL":
                    price = self.typical_size_price
                case _:
                    price = self.extended_size_price
                    available = False

            # Remove variants if more than 100
            if variant_count > 100:
                print("TOO MANY VARIANTS, MAXIMUM 100. SKIPPING REMAINING VARIANTS")
                continue

            # Split variants into light and dark colors
            if variant['options']['color'] in ["White", "Sport Grey"]:
                light_variant_ids.append(variant['id'])
            else:
                dark_variant_ids.append(variant['id'])

            # Append variant to return response
            return_response.append({
                'id': variant['id'],
                "price": price,
                "is_enabled": available,
                "is_default": default_variant
            })
            variant_count += 1
        return return_response, light_variant_ids, dark_variant_ids

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def get_shipping_costs(self, blueprint_id, print_provider_id):
        """Given a product ID, print provider id, and variants, get USA shipping costs for each variant"""
        url = f"{self.BASE_URL}/catalog/blueprints/{
            blueprint_id}/print_providers/{print_provider_id}/shipping.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch shipping costs. Status code: {
                  response.status_code}")

        for shipping_cost in response.json().get("profiles"):
            if "US" in shipping_cost.get("countries"):
                cost = shipping_cost.get("first_item").get("cost")
                return cost
        return None

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def upload_image(self, image_url: str):
        """Uploads an image to Printify and returns the URL."""
        url = f"{self.BASE_URL}/uploads/images.json"
        file_name = image_url.split("/")[-1]
        data = {
            "file_name": file_name,
            "url": image_url
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Image uploaded successfully: {file_name}")
            print("Image ID: ", response.json()['id'])
            return response.json()['id']
        else:
            print(f"Failed to upload image. Status code: {
                  response.status_code}")
            print(response.json())
            return None

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def create_product(
            self,
            blueprint_id,
            print_provider_id,
            variants,
            title,
            description,
            marketing_tags,
            text_colors=None,
            image_id=None,
    ):
        """
        Creates a new product on Printify.

        This function is decorated with:
        - @sleep_and_retry: Ensures that the function will retry after sleeping if a rate limit is hit.
        - @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD): Enforces the rate limit for the number of calls to the Printify API within a specified period.

        Args:
            blueprint_id (int): The ID of the blueprint for the product.
            print_provider_id (int): The ID of the print provider.
            variants (list): A list of variants for the product.
            title (str): The title of the product.
            description (str): The description of the product.
            marketing_tags (list): A list of marketing tags for the product.
            text_colors (list, optional): A list of text colors for the product. Defaults to None.
            image_id (str, optional): The ID of the image for the product. Defaults to None.

        Returns:
            product_id (str): The ID of the created product. or None if the product creation failed.
        """
        url = f"{self.BASE_URL}/shops/{self.store_id}/products.json"

        if image_id is not None and text_colors is not None:
            raise ValueError("Cannot provide both image_id and text_colors")

        print_areas = []
        if image_id is not None:
            print_areas = [
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
        else:
            for color in text_colors:
                text_image_id = color.get("image_id")
                print_areas.append(
                    {
                        "variant_ids": color.get("variant_ids"),
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": text_image_id,
                                        "x": 0.5,
                                        "y": 0.5,
                                        "scale": 1,
                                        "angle": 0
                                    }
                                ]

                            }
                        ]
                    }
                )

        product = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "tags": marketing_tags,
            "variants": variants,
            "print_areas": print_areas
            # TODO - Not working as expected!!
            # "sales_channel_properties": {
            #     "free_shipping": False,
            #     "collections": ["test"]
            # }
        }
        response = requests.post(url, headers=self.headers, json=product)
        if response.status_code == 200:
            print(f"Product created successfully: {response.json()['id']}")
            return response.json()['id']
        else:
            print(f"Failed to create product. Status code: {
                  response.status_code}")
            return None

    @sleep_and_retry
    @limits(calls=PUBLISH_RATE_LIMIT, period=PUBLISH_RATE_PERIOD)
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
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Product published: {product_id}")
        else:
            print(f"Failed to publish product. Status code: {
                  response.status_code}")

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def get_product_by_id(self, product_id):
        """Fetches a product by ID from the Printify API."""
        url = f"{self.BASE_URL}/shops/{self.store_id}/products/{product_id}.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            print(f"Successfully fetched product: {product_id}")
            return response.json()
        print(f"Failed to fetch product. Status code: {response.status_code}")

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def update_product_by_id(self, product_id, product):
        """Updates a product by ID in Printify."""
        url = f"{self.BASE_URL}/shops/{self.store_id}/products/{product_id}.json"
        response = requests.put(url, headers=self.headers, json=product)
        if response.status_code == 200:
            print(f"Product updated successfully: {product_id}")
        else:
            print(f"Failed to update product. Status code: {
                  response.status_code}")
            print(response.json())

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def remove_unavailable_variants(self, product_id):
        """Removes unavailable variants from a product."""
        product = self.get_product_by_id(product_id)
        variants = product['variants']
        for variant in variants:
            available = variant.get("is_available")
            enabled = variant.get("is_enabled")
            if not available and enabled:
                enabled = False
            variant["is_enabled"] = enabled
        self.update_product_by_id(product_id, {"variants": variants})
        return variants

    @sleep_and_retry
    @limits(calls=PRINTIFY_RATE_LIMIT, period=PRINTIFY_RATE_PERIOD)
    def only_front_product_images_by_product_id(self, product_id):
        """Removes all but the front images from a product."""
        product = self.get_product_by_id(product_id)

        images = product.get("images")
        for image in images:
            if image.get("position") != "front":
                images.remove(image)
        self.update_product_by_id(product_id, {"images": images})


if __name__ == "__main__":
    printify = PrintifyUtil()
    BLUEPRINT_ID = 6
    PRINT_PROVIDER_ID = 99
    VARIANTS = printify.get_all_variants(BLUEPRINT_ID, PRINT_PROVIDER_ID)
    IMAGE_ID = printify.upload_image(getenv("TEST_IMAGE_URL"))
    PRODUCT_ID = printify.create_product(
        blueprint_id=BLUEPRINT_ID,
        print_provider_id=PRINT_PROVIDER_ID,
        variants=VARIANTS,
        image_id=IMAGE_ID,
        title="Variant testing",
        description="TEST",
        marketing_tags=["TEST"]
    )
    printify.remove_unavailable_variants(PRODUCT_ID)
    printify.publish_product(PRODUCT_ID)
