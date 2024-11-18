"""FastAPI server that handles patterns and ideas."""
import os
import json
import uuid
from datetime import datetime
from urllib.parse import quote

from util.printify.printify_util import PrintifyUtil
from util.ai_util import AiUtil
from util.image_util import create_text_image
from util.github_util import GithubUploader
from util.general_util import remove_surrounding_quotes
from res.models.tshirt import TshirtFromAiList
from res.prompts.tshirt import user_message, blueprint_6_description


# Function to process patterns and idea
def process_patterns_and_idea(number_of_patterns, idea):
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

    # Create images and push to GitHub
    for pattern in patterns:
        # Generate a UUID for the pattern
        pattern["uuid"] = str(uuid.uuid4())
        pattern["tshirt_text"] = remove_surrounding_quotes(
            pattern["tshirt_text"])

        # Format the date and time as a string
        folder_name = f"./img/{current_time.strftime('%Y-%m-%d_%H-%M-%S')}"

        # Create the directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Generate image for each color
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

    # Upload the images to GitHub
    directory_with_images = f"{folder_name}/"
    github_repository_url = os.getenv("GH_UPLOAD_REPO")
    personal_access_token = os.getenv("GH_PAT")
    print(directory_with_images, github_repository_url)
    uploader = GithubUploader(
        directory_with_images,
        github_repository_url,
        personal_access_token
    )
    uploader.upload()

    # Send the images to Printify
    url_prefix = os.getenv("GH_CONTENT_PREFIX")
    for pattern in patterns:
        # Upload image to Printify
        for color in text_colors:
            hex_value = color.get("hex")
            image_url = f"{url_prefix}/{current_time.strftime('%Y-%m-%d_%H-%M-%S')}/{
                quote(pattern.get('uuid'))}{hex_value}.png"
            print("Image URL", image_url)
            image_id = printify.upload_image(image_url)
            # Append the image_id to the text color
            color["image_id"] = image_id

        # Create product in Printify
        product = printify.create_product(
            blueprint_id=blueprint,
            print_provider_id=printer,
            variants=variants,
            title=pattern.get("product_name"),
            description=pattern.get("description"),
            marketing_tags=pattern.get("marketing_tags"),
            text_colors=text_colors
        )

        # Add the product_id and image_ids to the pattern
        pattern.update({
            "product_id": product,
            "image_ids": [color.get("image_id") for color in text_colors]
        })

        # Remove all images except the front image
        printify.only_front_product_images_by_product_id(product)

        # Publish the product
        #printify.publish_product(product)

    return patterns
