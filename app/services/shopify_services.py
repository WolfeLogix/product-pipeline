"""This file sets the Taxonomy Node ID for all products in the Shopify store to T-Shirts."""
import time
from os import getenv
import requests

# Replace these with your actual store details
SHOPIFY_STORE_URL = f'https://{getenv("SHOPIFY_SHOP_NAME")
                               }.myshopify.com/admin/api/2024-01/graphql.json'
ACCESS_TOKEN = getenv('SHOPIFY_API_ACCESS_TOKEN')

# Headers for authentication
HEADERS = {
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': ACCESS_TOKEN
}


def fetch_products(cursor=None):
    query = '''
    query ($cursor: String) {
        products(first: 100, after: $cursor) {
            edges {
                node {
                    id
                    title
                    productType
                    productCategory {
                        productTaxonomyNode {
                            id
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
    return response.json()['data']['products']


def update_product_category(product_id, taxonomy_node_id):
    mutation = '''
    mutation {
        productUpdate(input: {
            id: "%s",
            productCategory: {
                productTaxonomyNodeId: "%s"
            }
        }) {
            product {
                id
                productCategory {
                    productTaxonomyNode {
                        id
                    }
                }
            }
            userErrors {
                field
                message
            }
        }
    }
    ''' % (product_id, taxonomy_node_id)
    response = requests.post(
        SHOPIFY_STORE_URL, headers=HEADERS, json={'query': mutation})
    response.raise_for_status()
    return response.json()


def update_uncategorized_products():
    cursor = None
    tshirt_taxonomy_node_id = 'gid://shopify/ProductTaxonomyNode/9532'
    while True:
        products_data = fetch_products(cursor)
        for edge in products_data['edges']:
            product = edge['node']
            product_id = product['id']
            title = product['title']
            product_type = product['productType']
            current_category = product['productCategory']
            current_taxonomy_node_id = current_category['productTaxonomyNode'][
                'id'] if current_category and current_category['productTaxonomyNode'] else None

            print(f"Product: {title}, Type: {product_type}")
            # Check if the product has no taxonomy node ID
            if not current_taxonomy_node_id:
                if product_type == "T-Shirt":
                    print(
                        f"Assigning taxonomy node ID '{tshirt_taxonomy_node_id}' to product '{
                            title}' (Type: {product_type})"
                    )
                    update_response = update_product_category(
                        product_id, tshirt_taxonomy_node_id)
                    if 'errors' in update_response:
                        print(
                            f"Error updating product '{title}': {update_response['errors']}")
                    else:
                        print(f"Product '{title}' updated successfully.")
                else:
                    print(
                        f"Product '{title}' (Type: {product_type}) has no taxonomy node and does not match 'T-Shirt'. Skipping.")

            # Respect Shopify's API rate limits
            time.sleep(0.5)

        if not products_data['pageInfo']['hasNextPage']:
            break
        cursor = products_data['edges'][-1]['cursor']


def set_taxonomy_nodeID():
    """This method retrieves uncategorized products from the Shopify store and sets their taxonomy node ID to T-Shirts."""
    # Replace this with the actual taxonomy node ID for T-Shirts
    update_uncategorized_products()
    return "ok"
