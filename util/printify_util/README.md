# Printify Utility Documentation

This guide provides a step-by-step walkthrough on how to use the Printify utility to create and publish products programmatically.

## Table of Contents

- [Printify Utility Documentation](#printify-utility-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Basic Setup](#basic-setup)
  - [Select a Blueprint](#select-a-blueprint)
  - [Get Print Providers](#get-print-providers)
  - [Get Variants](#get-variants)
  - [Upload Images](#upload-images)
  - [Create a Product](#create-a-product)
  - [Publish the Product](#publish-the-product)
  - [Additional Resources](#additional-resources)

## Introduction

The Printify utility simplifies interactions with the Printify API, allowing you to automate product creation and publishing directly from your code. This guide will help you set up the utility, select product templates, upload images, and publish products.

## Basic Setup

Initialize the Printify utility to establish API connections with Shopify and Printify.

```python
# Initialize Shopify and Printify API connections
printify = printify_util()
```

**Note:** Ensure that you have the necessary API keys and credentials configured within the `printify_util` class.

## Select a Blueprint

Blueprints are product templates that define the type of product you want to create (e.g., T-shirts, mugs).

To select a blueprint, specify its ID. For example, the Unisex Gildan T-Shirt has a blueprint ID of `6`.

```python
# Manually select blueprint (6 = Unisex Gildan T-Shirt)
BLUEPRINT_ID = 6
```

You can retrieve a list of available blueprints via the Printify API if needed.

## Get Print Providers

Print providers are companies that fulfill and ship your products. Retrieve a list of print providers available for the selected blueprint.

```python
# Get a list of print providers for the blueprint
providers = printify.get_all_providers(BLUEPRINT_ID)
```

Select a print provider by specifying its ID. For example, to choose the print provider with ID `99`:

```python
# Manually select a print provider (e.g., 99)
PRINT_PROVIDER_ID = 99
```

You can inspect the `providers` variable to see details about each provider and make an informed choice.

## Get Variants

Variants represent different options for your product, such as sizes and colors.

Retrieve the list of available variants for the selected blueprint and print provider:

```python
# Get a list of variants for the blueprint and print provider
variants = printify.get_all_variants(BLUEPRINT_ID, PRINT_PROVIDER_ID)
```

You can filter or modify the `variants` list to include only the variants you want to offer.

Optionally, retrieve shipping costs for each variant:

```python
# Get shipping costs (optional)
# shipping_cost = printify.get_shipping_costs(BLUEPRINT_ID, PRINT_PROVIDER_ID)
```

## Upload Images

Upload your product images to Printify by providing the URL of the image you wish to upload.

```python
# Upload images to Printify
image_url = "https://raw.githubusercontent.com/yourusername/yourrepo/main/image.png"
image_id = printify.upload_image(image_url)
```

The `upload_image` method returns an `image_id` that you will use when creating the product.

**Note:** Replace the `image_url` with the actual URL of your image.

## Create a Product

Create a new product in Printify using the blueprint, print provider, variants, and uploaded image.

```python
# Create product in Printify
PRODUCT_ID = printify.create_product(
    blueprint_id=BLUEPRINT_ID, 
    print_provider_id=PRINT_PROVIDER_ID, 
    variants=variants, 
    image_id=image_id
)
```

Ensure that you pass the correct `image_id` obtained from the image upload step.

## Publish the Product

Publish the created product to make it available for purchase. Be mindful of Printify's rate limits when publishing products (maximum of 200 products per 30 minutes, or 1 every 10 seconds).

```python
# Publish product in Printify
printify.publish_product(PRODUCT_ID)
```

## Additional Resources

- [Printify API Documentation](https://developers.printify.com/)
- [Printify Blueprint IDs](https://developers.printify.com/#blueprints)
- [Printify Print Providers](https://developers.printify.com/#print-providers)