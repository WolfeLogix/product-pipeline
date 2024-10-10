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

Run the following command to generate the required `.env` file. Replace the empty strings with the appropriate values.

```bash
cat <<EOF > .env
PRINTIFY_API_KEY=""
OPENAI_API_KEY=""
GITHUB_PAT=""
GITHUB_UPLOAD_REPO=""
GITHUB_UPLOAD_PREFIX=""
EOF
```

Additionally, the shopify utility requires these envronment variables to be set:

```bash
echo 'SHOPIFY_API_KEY=""' >> .env
echo 'SHOPIFY_API_SECRET=""' >> .env
echo 'SHOPIFY_SHOP_NAME=""' >> .env
```


## Running Tests

Formal unit tests are not yet implemented. However, all the functions have a manual test if you run the script directly.

### Main Project

`clear && flake8 --ignore=E501 --exclude=.venv`  

### Image Utility

`python3.12 image_util.py`  

### AI Utility

`python3.12 ai_util.py`  
