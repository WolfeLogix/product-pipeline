import time
import requests
from os import getenv

# Shopify store details
SHOPIFY_STORE_URL = f'https://{getenv("SHOPIFY_SHOP_NAME")
                               }.myshopify.com/admin/api/2024-01/graphql.json'
ACCESS_TOKEN = getenv('SHOPIFY_API_ACCESS_TOKEN')

# Headers for authentication
HEADERS = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': ACCESS_TOKEN
}


def fetch_products(cursor=None):
    """Fetch products from Shopify using GraphQL with optional pagination."""
    query = '''
    query ($cursor: String) {
        products(first: 100, after: $cursor) {
            edges {
                node {
                    id
                    title
                    metafields(first: 100) {
                        edges {
                            node {
                                namespace
                                key
                                value
                            }
                        }
                    }
                }
                cursor
            }
            pageInfo {
                hasNextPage
            }
        }
    }
    '''
    variables = {'cursor': cursor}
    response = requests.post(SHOPIFY_STORE_URL, headers=HEADERS, json={
                             'query': query, 'variables': variables})
    response.raise_for_status()
    json_response = response.json()

    # Check for errors
    if 'errors' in json_response:
        raise ValueError(f"GraphQL errors during fetch: {
                         json_response['errors']}")
    if 'data' not in json_response or 'products' not in json_response['data']:
        raise ValueError(f"Unexpected response format: {json_response}")

    return json_response['data']['products']


def update_product_metafields(product_id, metafields):
    """Update metafields for a specific product."""
    mutation = '''
    mutation UpdateProductMetafields($input: ProductInput!) {
        productUpdate(input: $input) {
            product {
                id
                metafields(first: 100) {
                    edges {
                        node {
                            namespace
                            key
                            value
                        }
                    }
                }
            }
            userErrors {
                field
                message
            }
        }
    }
    '''
    variables = {
        "input": {
            "id": product_id,
            "metafields": metafields
        }
    }
    response = requests.post(SHOPIFY_STORE_URL, headers=HEADERS, json={
                             'query': mutation, 'variables': variables})
    response.raise_for_status()
    json_response = response.json()

    # Check for errors
    if 'errors' in json_response:
        raise ValueError(f"GraphQL errors during update: {
                         json_response['errors']}")

    data = json_response.get('data', {})
    product_update = data.get('productUpdate', {})
    user_errors = product_update.get('userErrors', [])
    if user_errors:
        raise ValueError(f"User errors returned: {user_errors}")

    product = product_update.get('product')
    if not product:
        raise ValueError(f"No product returned after update: {json_response}")

    return product


def update_all_products_google_fields():
    """Iterate through all products, print all metafields, and update Google fields to Unisex/Adult."""
    cursor = None
    while True:
        products_data = fetch_products(cursor)
        for edge in products_data['edges']:
            product = edge['node']
            product_id = product['id']
            title = product['title']
            print(f"Product: {title} (ID: {product_id})")

            # Print all existing metafields
            metafields = product.get('metafields', {}).get('edges', [])
            if not metafields:
                print("  No metafields found.")
            else:
                for metafield_edge in metafields:
                    metafield = metafield_edge['node']
                    print(f"  Metafield - Namespace: {metafield['namespace']}, Key: {
                          metafield['key']}, Value: {metafield['value']}")

            # Prepare metafields to update
            metafields_to_update = [
                {
                    "namespace": "mm-google-shopping",
                    "key": "gender",
                    "value": "Unisex",
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "mm-google-shopping",
                    "key": "age_group",
                    "value": "Adult",
                    "type": "single_line_text_field"
                }
            ]

            # Update metafields
            updated_product = update_product_metafields(
                product_id, metafields_to_update)
            print(f"Updated Product: {updated_product['id']} with Metafields:")
            for mf in updated_product['metafields']['edges']:
                node = mf['node']
                print(f"  - {node['namespace']
                             }.{node['key']}: {node['value']}")

            # Respect Shopify API rate limits
            time.sleep(0.5)

        if not products_data['pageInfo']['hasNextPage']:
            break
        cursor = products_data['edges'][-1]['cursor']





def set_google_attributes():
    update_all_products_google_fields()
    return "ok"
