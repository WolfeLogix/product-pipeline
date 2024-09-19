from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, color, height, width):
    # Create a blank transparent image
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", size=20)  # Change size as needed
    except IOError:
        font = ImageFont.load_default()
    
    # Split the text into lines that fit within the specified width
    wrapped_text = []
    lines = text.splitlines()
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            # Check if adding the next word would exceed the width
            test_line = f"{current_line} {word}".strip()
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]  # Calculate width from bbox
            if text_width <= width:
                current_line = test_line
            else:
                wrapped_text.append(current_line)
                current_line = word
        wrapped_text.append(current_line)  # Add the last line

    # Calculate total height for the wrapped text
    total_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text)
    
    # Center position for the text
    y_offset = (height - total_height) / 2
    
    # Draw the text on the image
    for line in wrapped_text:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Calculate width from bbox
        x = (width - text_width) / 2  # Center horizontally
        draw.text((x, y_offset), line, fill=color, font=font)
        y_offset += text_bbox[3] - text_bbox[1]  # Move down for the next line
    
    # Save the image
    image.save("output_image.png", "PNG")

# Example usage:
create_text_image("This is a sample text to demonstrate text wrapping.", "#FF5733", 200, 400)
