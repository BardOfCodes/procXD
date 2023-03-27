"""Module providing random_hex_color and sample_color."""
import colorsys
import random

RANDOM_PALLETE = [
    "#EF476F",
    "#FFD166",
    "#06D6A0",
    "#118AB2",
    "#073B4C",
    "#FC5185",
    "#FFCE66",
    "#6EC4E8",
    "#4B4E6D",
    "#E8AEB7",
    "#EDC7B7",
    "#FF8A5B",
    "#F4C2C2",
    "#8E6C88",
    "#BDBDBD",
    "#EDF5E1",
    "#F7FFF7",
    "#218380",
    "#FFA500",
    "#FFC0CB",
    "#8B0000",
    "#FF4500",
    "#FFA07A",
    "#FF1493",
    "#FF69B4",
    "#FFD700",
    "#DC143C",
    "#00FF00",
    "#4169E1",
    "#FF00FF",
    "#BA55D3",
    "#00FA9A",
    "#00FFFF",
    "#FFB6C1",
    "#9ACD32",
    "#FFFF00",
    "#FF7F50",
    "#8A2BE2",
    "#00BFFF",
    "#FF00FF",
    "#FF69B4",
    "#FFFF00",
    "#8B008B",
    "#00FFFF",
    "#000080",
    "#FF7F50",
    "#FFDAB9",
    "#FFFFE0",
    "#FFE4E1",
    "#C0C0C0",
    "#808080",
]


def sample_color(color_hex):
    """
    Given a hex color as input, samples a new color that is 45 to 135 degrees apart from
    the input color_hex in HSV space, while also ensuring that the luminance is high enough
    for contrast with black text. Returns the resulting color in hex format.

    Args:
        color_hex (str): A hex color string of the format "#RRGGBB".

    Returns:
        str: A hex color string of the format "#RRGGBB" representing the resulting color.
    """
    # Convert input color to HSV
    color_rgb = tuple(int(color_hex.lstrip(
        "#")[i: i + 2], 16) for i in (0, 2, 4))
    color_hsv = colorsys.rgb_to_hsv(*color_rgb)

    # Sample a new color 45 to 135 degrees apart in HSV space
    new_hue = color_hsv[0] + 0.25 + (0.5 * random.random())
    if new_hue > 1:
        new_hue -= 1
    new_saturation = max(color_hsv[1] - 0.1, 0)
    new_value = min(color_hsv[2] + 0.1, 1)
    new_color_hsv = (new_hue, new_saturation, new_value)

    # Convert new color back to RGB and calculate its luminance
    new_color_rgb = colorsys.hsv_to_rgb(*new_color_hsv)
    red, green, blue = tuple(int(c * 255) for c in new_color_rgb)
    luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255

    # If the luminance is too low, adjust the brightness,
    # until it meets the contrast ratio requirement
    while (luminance + 0.05) / (0 + 0.05) < 4.5:
        if new_color_hsv[2] < 0.5:
            new_color_hsv = (
                new_color_hsv[0],
                new_color_hsv[1],
                min(new_color_hsv[2] + 0.1, 1),
            )
        else:
            new_color_hsv = (
                new_color_hsv[0],
                new_color_hsv[1],
                max(new_color_hsv[2] - 0.1, 0),
            )
        new_color_rgb = colorsys.hsv_to_rgb(*new_color_hsv)
        red, green, blue = tuple(int(c * 255) for c in new_color_rgb)
        luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255

    # Convert new color to hex and return
    new_color_hex = f"#{int(red):02x}{int(green):02x}{int(blue):02x}"
    return new_color_hex


def random_hex_color():
    """Generate a random hex color with a luminance of at least 4.5:1 with black text.

    Returns:
        str: A hex color string of the format "#RRGGBB" representing the resulting color.
    """
    while True:
        # generate a random hex color
        color = "#" + "".join(random.choices("0123456789ABCDEF", k=6))
        # calculate the luminance of the color
        red, green, blue = tuple(int(color[i: i + 2], 16) for i in (1, 3, 5))
        luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255
        # check if the contrast ratio with black text is at least 4.5:1
        if (luminance + 0.05) / (0 + 0.05) >= 4.5:
            return color
