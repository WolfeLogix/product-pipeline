# Product Pipeline

This project is an ai based data pipeline. You start by suppling an idea for a category of t-shirt. When the pipeline runs, it does a number of things:

- generates `p` number of patterns using the supplied `idea`
- generates an image with a transparent background with the generated text
- uploads these images to github
- lists and publishes all the new patterns on printify

From there, Printify takes over and the following things happen

- products are synced with shopify, and a number of other retailers
- orders are automatically sent to the print provider when a sale is made

## Reuqired Environment Variables

- PRINTIFY_API_KEY
- OPENAI_API_KEY
- SHOPIFY_API_KEY
- SHOPIFY_API_SECRET
- SHOPIFY_SHOP_NAME
