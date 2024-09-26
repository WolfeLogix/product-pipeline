
import os
import argparse
import uuid
import random
import json
from datetime import datetime

from util.printify_util import printify_util
from util.ai_util import ai_util
from util.image_util import create_text_image
from res.models.tshirt import tshirt_from_ai, tshirt_from_ai_list
from util.github_util import GithubUploader

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Set up argument parser
parser = argparse.ArgumentParser(description="Utility to handle patterns and ideas.")
parser.add_argument('-p', '--patterns', type=int, default=10, 
                    help='Number of patterns, default is 10')
parser.add_argument('idea', type=str, 
                    help='The Idea to generate patterns for')
parser.add_argument('-t', '--tags', type=lambda s: [tag.strip() for tag in s.split(',')],
                    help='Optional comma-delimited list of tags')

# Random Seeding
current_time = int(datetime.now().timestamp())
random.seed(current_time)


def main():
    # Parse the arguments
    args = parser.parse_args()
    idea = args.idea
    number_of_patterns = args.patterns
    tags = args.tags

    # AI prompt
    prompt = [
        {"role": "system", "content": "You are a helpful chatbot"},
        {"role": "user", "content": idea} #TODO - fix this, ie "make x number of patterns for y idea"
    ]

    # Initialize AI
    ai = ai_util()

    response = ai.chat(
        messages = prompt,
        output_model=tshirt_from_ai_list,
    )
    # Parse the response
    print(response)
    print(type(response))
    parsed_response = json.loads(response)
    patterns = parsed_response['patterns']



    for pattern in patterns:
        print(pattern) #[{pattern.title, pattern.description, pattern.tshirt_text}]


        # generate filename
        # filename = uuid.uuid5(uuid.NAMESPACE_DNS, random.getrandbits(128)) #TODO - broken
        
        # Get the current date and time
        current_time = datetime.now()

        # Format the date and time as a string
        folder_name = current_time.strftime("%Y-%m-%d_%H-%M-%S")

        # Create the directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # generate image
        create_text_image(
            text=pattern.get("tshirt_text"),
            height=1000,
            width=1000,
            file_name=f"img/{folder_name}/{pattern.get('title')}.png",
            color="#000000"
        ) #TOOD = make both white text and black text version of this
        # upload the image

        directory_with_images = '/path/to/your/images'
        github_repository_url = 'https://github.com/yourusername/yourrepo.git'
        personal_access_token = os.getenv('GITHUB_PAT')
        uploader = GithubUploader(directory_with_images, github_repository_url, personal_access_token)
        uploader.upload()
        # create product in printify



    # # --- Basic Setup ---#
    # # Initialize Shopify and Printify API connections
    # printify = printify_util()

    # # Manually Select Blueprint (6 = Unisex Gildan T-Shirt)
    # BLUEPRINT_ID = 6

    # # Query to get a list of print providers for the blueprint
    # providers = printify.get_all_providers(BLUEPRINT_ID)
    # PRINT_PROVIDER_ID = 99

    # # Query to get a list of variants for the blueprint
    # variants = printify.get_all_variants(BLUEPRINT_ID, PRINT_PROVIDER_ID)

    # # Query to get a list of shipping costs for each variant
    # shipping_cost = printify.get_shipping_costs(BLUEPRINT_ID, PRINT_PROVIDER_ID)


    # # --- Per Product Setup ---#
    # ## FOR IMAGE IN SPREADSHEET:
    # # Needed: title, description, image_url

    # # # Upload Images to Printify / Github
    # # image_url = "https://raw.githubusercontent.com/parishwolfe/product-pipeline/refs/heads/main/HelloWorld_white.png"
    # # printify.upload_image(image_url)

    # # Create Product in Printify
    # PRODUCT_ID = printify.create_product(
    #     blueprint_id=BLUEPRINT_ID, 
    #     print_provider_id=PRINT_PROVIDER_ID, 
    #     variants=variants, 
    #     image_id="66eb5eb5557b6ed02c9276aa"
    # )

    # # Publish Product in Printify (Rate Limited to 200/30min or 1 per 10 seconds)
    # printify.publish_product(PRODUCT_ID)

if __name__ == "__main__":
    main()