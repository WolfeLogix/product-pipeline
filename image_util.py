from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, color, height, width, file_name):
    # Create a blank transparent image
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Font parameters
    min_font_size = 1
    max_font_size = 500  # Set an upper limit for font size

    best_font_size = min_font_size
    best_wrapped_text = None
    best_total_height = None

    while min_font_size <= max_font_size:
        font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype("arial.ttf", size=font_size)
        fits, wrapped_text, total_height = does_text_fit(draw, text, font, width, height)
        if fits:
            # This font size fits, try a bigger one
            best_font_size = font_size
            best_wrapped_text = wrapped_text
            best_total_height = total_height
            min_font_size = font_size + 1
        else:
            # Font size too big, try a smaller one
            max_font_size = font_size - 1

    if best_wrapped_text is None:
        # Text does not fit even at the minimum font size
        raise ValueError("Text cannot fit into the image at the minimum font size.")

    # Use the best font size
    font = ImageFont.truetype("arial.ttf", size=best_font_size)

    # Center position for the text
    y_offset = (height - best_total_height) / 2

    # Draw the text on the image
    for line in best_wrapped_text:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width - text_width) / 2  # Center horizontally
        draw.text((x, y_offset), line, fill=color, font=font)
        line_height = text_bbox[3] - text_bbox[1]
        y_offset += line_height  # Move down for the next line
    
    # Save the image
    image.save(file_name, "PNG")

def does_text_fit(draw, text, font, width, height):
    # Wrap the text
    wrapped_text = []
    lines = text.splitlines()
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= width:
                current_line = test_line
            else:
                if current_line == "":
                    # Single word longer than width, cannot fit
                    return False, None, None
                wrapped_text.append(current_line)
                current_line = word
        if current_line != "":
            wrapped_text.append(current_line)

    # Calculate total height for the wrapped text
    line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text]
    total_height = sum(line_heights)

    # Check if any line exceeds width
    any_line_too_wide = any(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] > width for line in wrapped_text)

    # Return whether text fits, the wrapped_text, and total_height
    fits = (total_height <= height) and not any_line_too_wide
    return fits, wrapped_text, total_height

# Example usage:
create_text_image("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "#FF5733", 800, 1200, "test_1.png")
create_text_image("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "#FF5733", 800, 400, "test_2.png")
create_text_image("Lorem ipsum dolor sit amet", "#FF5733", 800, 1200, "test_3.png")
create_text_image("Lorem ipsum dolor sit amet", "#FF5733", 800, 400, "test_4.png")
