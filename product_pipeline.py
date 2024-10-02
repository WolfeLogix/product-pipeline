
import os
import argparse
import random
import json
from datetime import datetime

from util.printify_util.printify_util import printify_util
from util.ai_util import ai_util
from util.image_util import create_text_image
from res.models.tshirt import tshirt_from_ai_list
from res.prompts.tshirt import user_message
from util.github_util import GithubUploader

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Set up argument parser
parser = argparse.ArgumentParser(description="Utility to handle patterns and ideas.")
parser.add_argument('-p', '--patterns', type=int, default=3, 
                    help='Number of patterns, default is 10')
parser.add_argument('idea', type=str, 
                    help='The Idea to generate patterns for')

# Random Seeding
current_time = int(datetime.now().timestamp())
random.seed(current_time)


def main():
    # Parse the arguments
    args = parser.parse_args()
    idea = args.idea
    number_of_patterns = args.patterns

    # Initialize AI
    ai = ai_util()

    # Initialize and set up Printify
    printify = printify_util()
    blueprint = 6  # Unisex Gildan T-Shirt
    printer = 99 # Printify Choice Provider
    variants = printify.get_all_variants(blueprint, printer)

    # Get patterns from AI
    response = ai.chat(
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": user_message % (number_of_patterns, idea)}
        ],
        output_model=tshirt_from_ai_list,
    ) #TODO - TEST TO MAKE SURE THIS WORKS using both f string and %s formatting

    # Parse the response
    parsed_response = json.loads(response)
    patterns = parsed_response['patterns']

    # Create images and push to github
    for pattern in patterns:
        print(pattern) #[{pattern.title, pattern.description, pattern.tshirt_text}]
        # Get the current date and time
        current_time = datetime.now()

        # Format the date and time as a string
        folder_name = f"./img/{current_time.strftime("%Y-%m-%d_%H-%M-%S")}"

        # Create the directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # generate image
        create_text_image(
            text=pattern.get("tshirt_text"),
            height=1000,
            width=1000,
            file_name=f"./{folder_name}/{pattern.get('title')}.png",
            color="#000000"
        ) #TOOD = make both white text and black text version of this


    # upload the images to github
    directory_with_images = f"{folder_name}/"
    github_repository_url = os.getenv("GITHUP_UPLOAD_REPO")
    personal_access_token = os.getenv("GITHUB_PAT")
    print(directory_with_images, github_repository_url, personal_access_token)
    uploader = GithubUploader(
        directory_with_images, 
        github_repository_url, 
        personal_access_token
    )
    uploader.upload()

    # Send the images to Printify
    url_prefix = os.getenv("GITHUB_URL_PREFIX")
    for pattern in patterns:
        # Upload Image to Printify
        image_url = f"{url_prefix}/{folder_name}/{pattern.get('title')}.png"
        image_id = printify.upload_image(image_url)

        # Create Product in Printify
        product = printify.create_product(
            blueprint_id=blueprint,
            print_provider_id=printer,
            variants=variants,
            image_id=image_id
        )

        # Publish the product
        printify.publish_product(product)

if __name__ == "__main__":
    main()