import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageMath
from colour import Color


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def centerSquareCrop(image_file):
    img = Image.open(image_file)
    width, height = img.size
    new_dimension = min((width, height))

    left = (width - new_dimension) / 2
    top = (height - new_dimension) / 2
    right = (width + new_dimension) / 2
    bottom = (height + new_dimension) / 2

    img = img.crop((left, top, right, bottom))
    img.save(image_file)


def asciiArt(image_file, output_file, scale=0, bg=(0, 0, 0)):
    # Covnert bg to color object
    bg = Color(rgb=bg)

    # Open file
    img = Image.open(image_file)
    img.load()

    # Scale
    if scale == 0:
        scale = 36 / img.size[0]

    # Array of chars from dense to sparse
    chars = list('$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ')

    # Compute aspect ratio of font width/height
    font = ImageFont.load_default()
    font_width, font_height = font.getsize('X')

    # Resize image to match font aspect ratio
    letter_width = round(img.size[0] * scale * (font_height / font_width))
    letter_height = round(img.size[1] * scale)
    img = img.resize((letter_width, letter_height))

    # Convert image to RGB
    img.convert('RGBA')
    temp = img.copy()
    img = Image.new('RGB', temp.size,
                    tuple(round(i * 255) for i in bg.get_rgb()))
    alpha = temp.convert('RGBA').split()[-1]
    img.paste(temp, mask=alpha)

    # Get a normalized grayscale version
    img_grayscale = img.convert(mode='L')
    img_grayscale = ImageOps.autocontrast(img_grayscale)

    # Invert if bg is near black
    if bg.get_luminance() < 0.5:
        img_grayscale = ImageOps.invert(img_grayscale)

    # Remap values to 0 to chars.size - 1
    img_grayscale = ImageMath.eval("a * factor / 255", {
        'a': img_grayscale,
        'factor': len(chars) - 1
    })

    # Generate ascii art
    rows = chunks(list(img_grayscale.getdata()), img_grayscale.size[0])
    rows = [''.join(chars[c] for c in row) for row in rows]

    # Create blank image and drawer
    newimg = Image.new(
        "RGB", (letter_width * font_width, letter_height * font_height),
        tuple(round(i * 255) for i in bg.get_rgb()))
    drawer = ImageDraw.Draw(newimg)

    color_generator = (i for i in img.getdata())
    y = 0
    for row in rows:
        x = 0
        for c in row:
            color = tuple(next(color_generator))
            drawer.text((x, y), c, color, font=font)
            x += font_width
            print(c, end='')
        y += font_height
        print()

    # print("Showing newimg")
    newimg.show()
    newimg.save(output_file)
    return rows


if __name__ == "__main__":
    scale = 1
    img_filename = None
    if (len(sys.argv) in (2, 3)):
        img_filename = sys.argv[1]
    else:
        img_filename = input("enter filename: ")

    if (len(sys.argv) == 3):
        scale = sys.argv[2]
    else:
        scale = input("enter scale: ")

    scale = float(scale)

    asciiArt(img_filename, 'out_' + img_filename, scale)