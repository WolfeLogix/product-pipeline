"""This is the main entrypoint for the application."""
import os
import argparse
import random
import json
import uuid
from datetime import datetime
from urllib.parse import quote

from dotenv import load_dotenv

from util.printify.printify_util import PrintifyUtil
from util.ai_util import AiUtil
from util.image_util import create_text_image
from util.github_util import GithubUploader
from res.models.tshirt import TshirtFromAiList
from res.prompts.tshirt import user_message, blueprint_6_description


# Load environment variables from .env file
load_dotenv('.env')

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Utility to handle patterns and ideas.")
parser.add_argument('-p', '--patterns', type=int, default=3,
                    help='Number of patterns, default is 3')
parser.add_argument('idea', type=str,
                    help='The Idea to generate patterns for')

# Random Seeding
random.seed(int(datetime.now().timestamp()))


def main():
    # Parse the arguments
    args = parser.parse_args()
    idea = args.idea
    number_of_patterns = args.patterns
    text_colors = [
        {"hex": "000000", "shade": "dark"},
        {"hex": "FFFFFF", "shade": "light"}
    ]

    # Initialize AI
    ai = AiUtil()

    # Initialize and set up Printify
    printify = PrintifyUtil()
    blueprint = 6  # Unisex Gildan T-Shirt
    printer = 99  # Printify Choice Provider
    variants, light_ids, dark_ids = printify.get_all_variants(
        blueprint, printer)
    # Apply the variant ids to the text colors
    for color in text_colors:
        if color.get("shade") == "light":
            color["variant_ids"] = dark_ids
        else:
            color["variant_ids"] = light_ids

    # Get patterns from AI
    response = ai.chat(
        messages=[
            {"role": "system", "content": "You are a helpful chatbot"},
            {"role": "user", "content": user_message %
                (number_of_patterns, idea) + blueprint_6_description},
        ],
        output_model=TshirtFromAiList,
    )

    # Parse the response
    parsed_response = json.loads(response)
    patterns = parsed_response['patterns']

    # Get the current date and time
    current_time = datetime.now()

    # Create images and push to github
    for pattern in patterns:
        # Generate a uuid for the pattern
        pattern["uuid"] = str(uuid.uuid4())

        # Format the date and time as a string
        folder_name = f"./img/{current_time.strftime("%Y-%m-%d_%H-%M-%S")}"

        # Create the directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # generate image for color
        for color in text_colors:
            hex_value = color.get("hex")
            create_text_image(
                text=pattern.get("tshirt_text"),
                height=2000,
                width=2000,
                file_name=f"{
                    folder_name}/{pattern.get('uuid')}{hex_value}.png",
                color="#" + hex_value
            )

    # Display the actual number of patterns generated
    print(f"\nNumber of Patterns generated: {len(patterns)}\n")

    # upload the images to github
    directory_with_images = f"{folder_name}/"
    github_repository_url = os.getenv("GITHUP_UPLOAD_REPO")
    personal_access_token = os.getenv("GITHUB_PAT")
    print(directory_with_images, github_repository_url)
    uploader = GithubUploader(
        directory_with_images,
        github_repository_url,
        personal_access_token
    )
    uploader.upload()

    # Send the images to Printify
    url_prefix = os.getenv("GITHUB_UPLOAD_PREFIX")
    for pattern in patterns:
        # Upload Image to Printify
        for color in text_colors:
            hex_value = color.get("hex")
            image_url = f"{url_prefix}/{current_time.strftime("%Y-%m-%d_%H-%M-%S")}/{
                quote(pattern.get('uuid'))}{hex_value}.png"
            print("Image URL", image_url)
            image_id = printify.upload_image(image_url)
            # Append the image_id to the text color
            color["image_id"] = image_id

        # Create Product in Printify
        product = printify.create_product(
            blueprint_id=blueprint,
            print_provider_id=printer,
            variants=variants,
            title=pattern.get("product_name"),
            description=pattern.get("description"),
            marketing_tags=pattern.get("marketing_tags"),
            text_colors=text_colors
        )

        # Publish the product
        printify.publish_product(product)


if __name__ == "__main__":
    main()
