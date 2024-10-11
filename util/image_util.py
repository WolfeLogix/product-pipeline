"""This is a utility class for creating images with text using the Pillow library."""
import os
import traceback
from PIL import Image, ImageDraw, ImageFont


def get_text_width(font, text):
    """Returns the width of the text when rendered with the given font."""
    if hasattr(font, 'getlength'):
        # For newer versions of Pillow
        return font.getlength(text)
    elif hasattr(font, 'getsize'):
        # For older versions of Pillow
        return font.getsize(text)[0]
    elif hasattr(font, 'getbbox'):
        # Alternative method
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]
    else:
        raise AttributeError(
            "Font object has no method to calculate text width.")


def create_text_image(text: str, height: int, width: int, file_name: str, color: str = "#000000"):
    """
    Creates an image with the specified text centered within the given
    dimensions and saves it as a PNG file.
    Args:
        text (str): The text to be displayed on the image.
        height (int): The height of the image in pixels.
        width (int): The width of the image in pixels.
        file_name (str): The name of the file to save the image as,
            including the file extension (e.g., 'image.png').
        color (str, optional): The color of the text in hexadecimal
            format (default is black, "#000000").
    Raises:
        ValueError: If the text cannot fit into the image at the minimum font size.
    Returns:
        str: The file name if the image was created successfully, None otherwise.
    """

    # Ensure the output directory exists
    output_dir = os.path.dirname(file_name)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Output directory created: {output_dir}")
        except Exception as e:
            print(f"Failed to create output directory: {output_dir}")
            traceback.print_exc()
            print(e)
            return None

    try:
        # Create a blank transparent image
        image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Font parameters
        min_font_size = 1
        max_font_size = 500  # Set an upper limit for font size

        best_font_size = min_font_size
        best_wrapped_text = None
        best_total_height = None

        # Function to find a font that exists on the system
        def find_font():
            possible_fonts = [
                # Common fonts on Mac
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Helvetica.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttf",
                "/Library/Fonts/Times New Roman.ttf",
                # Common fonts on Windows
                "C:\\Windows\\Fonts\\Arial.ttf",
                "C:\\Windows\\Fonts\\times.ttf",
                "C:\\Windows\\Fonts\\verdana.ttf",
                # Common fonts on Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                # PIL default font
                "arial.ttf",
                "DejaVuSans.ttf",  # Comes with matplotlib
            ]
            for font_path in possible_fonts:
                if os.path.exists(font_path):
                    return font_path
            # If none of the above fonts exist, use PIL's default font
            return None

        font_path = find_font()
        if font_path is None:
            # Use PIL's default font
            print("Using PIL's default font.")
            font = ImageFont.load_default()
        else:
            print(f"Using font: {font_path}")
            font = None  # We'll set the font in the loop

        while min_font_size <= max_font_size:
            font_size = (min_font_size + max_font_size) // 2
            if font_path is None:
                # Use default font
                font = ImageFont.load_default()
            else:
                font = ImageFont.truetype(font_path, size=font_size)

            fits, wrapped_text, total_height = does_text_fit(
                draw, text, font, width, height)
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
            raise ValueError(
                "Text cannot fit into the image at the minimum font size.")

        # Use the best font size
        if font_path is None:
            # Use default font
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, size=best_font_size)
        ascent, descent = font.getmetrics()
        line_spacing = int(best_font_size * 0.2)  # 20% of font size

        # Adjust total height to include the descent of the last line
        best_total_height += descent

        # Center position for the text
        y_offset = (height - best_total_height) / 2

        # Draw the text on the image
        for line in best_wrapped_text:
            # Get text width
            text_width = get_text_width(font, line)
            x = (width - text_width) / 2  # Center horizontally
            draw.text((x, y_offset), line, fill=color, font=font)
            y_offset += ascent + descent + line_spacing  # Move down for the next line

        # Save the image
        image.save(file_name, "PNG")
        print(f"Image saved successfully: {file_name}")
        return file_name

    except Exception as e:
        print(f"Failed to create image '{file_name}': {e}")
        traceback.print_exc()
        return None


def does_text_fit(draw, text, font, width, height):
    """Determines if the text fits within the specified width and height with the given font."""
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
            # Get text width
            text_width = get_text_width(font, test_line)
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
    total_height = (ascent + descent) * num_lines + \
        line_spacing * (num_lines - 1)

    # Check if any line exceeds width
    any_line_too_wide = any(get_text_width(font, line) > width for line in wrapped_text)

    # Return whether text fits, the wrapped_text, and total_height
    fits = (total_height <= height) and not any_line_too_wide
    return fits, wrapped_text, total_height


if __name__ == "__main__":
    # Example usage:
    text = '"Welcome to the Bug-Free Zone - Powered by Unit Tests"'
    file_name = "./img/Bug-Free Zone000000.png"

    # Specify image dimensions
    height = 800
    width = 1200  # Adjust as needed

    result = create_text_image(
        text,
        height,
        width,
        file_name,
        "#000000"
    )
    if result:
        print(f"Image created successfully: {result}")
    else:
        print("Image creation failed.")
