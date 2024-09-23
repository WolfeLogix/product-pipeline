from PIL import Image, ImageDraw, ImageFont

def create_text_image(text: str, height: int, width: int, file_name: str, color: str="#000000"):
    def create_text_image(text: str, height: int, width: int, file_name: str, color="#000000"):
        """
        Creates an image with the specified text centered within the given dimensions and saves it as a PNG file.
        Args:
            text (str): The text to be displayed on the image.
            height (int): The height of the image in pixels.
            width (int): The width of the image in pixels.
            file_name (str): The name of the file to save the image as, including the file extension (e.g., 'image.png').
            color (str, optional): The color of the text in hexadecimal format (default is black, "#000000").
        Raises:
            ValueError: If the text cannot fit into the image at the minimum font size.
        Returns:
            None
        """

    # Create a blank transparent image
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Font parameters
    min_font_size = 1
    max_font_size = 500  # Set an upper limit for font size

    best_font_size = min_font_size
    best_wrapped_text = None
    best_total_height = None

    # Load the font once to avoid repetitive loading
    font_path = "arial.ttf"  # Ensure this font is available on your system

    while min_font_size <= max_font_size:
        font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_path, size=font_size)

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
    font = ImageFont.truetype(font_path, size=best_font_size)
    ascent, descent = font.getmetrics()
    line_spacing = int(best_font_size * 0.2)  # 20% of font size

    # Adjust total height to include the descent of the last line
    best_total_height += descent

    # Center position for the text
    y_offset = (height - best_total_height) / 2

    # Draw the text on the image
    for line in best_wrapped_text:
        text_width = font.getlength(line)
        x = (width - text_width) / 2  # Center horizontally
        draw.text((x, y_offset), line, fill=color, font=font)
        y_offset += ascent + descent + line_spacing  # Move down for the next line

    # Save the image
    image.save(file_name, "PNG")

def does_text_fit(draw, text, font, width, height):
    ascent, descent = font.getmetrics()
    line_spacing = int(font.size * 0.2)  # 20% of font size

    # Wrap the text
    wrapped_text = []
    lines = text.splitlines()
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_width = font.getlength(test_line)
            if text_width <= width:
                current_line = test_line
            else:
                if not current_line:
                    # Single word longer than width, cannot fit
                    return False, None, None
                wrapped_text.append(current_line)
                current_line = word
        if current_line:
            wrapped_text.append(current_line)

    # Calculate total height for the wrapped text
    num_lines = len(wrapped_text)
    total_height = (ascent + descent) * num_lines + line_spacing * (num_lines - 1)

    # Check if any line exceeds width
    any_line_too_wide = any(font.getlength(line) > width for line in wrapped_text)

    # Return whether text fits, the wrapped_text, and total_height
    fits = (total_height <= height) and not any_line_too_wide
    return fits, wrapped_text, total_height

# Example usage:
create_text_image(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    800,
    1200,
    "img/test_1.png",
    "#000000"
)
create_text_image(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    800,
    400,
    "img/test_2.png",
    "#FF5733"
)
create_text_image("Lorem ipsum dolor sit amet", 800, 1200, "img/test_3.png")
create_text_image("Lorem ipsum dolor sit amet", 800, 400, "img/test_4.png", "#FFFFFF")
