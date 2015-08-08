# sudo pip install tinypng
# sudo apt-get install python-imaging
import os
import getopt
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageStat
from tinypng import shrink_file

# Required width for the images
BASE_WIDTH = 607
WATERMARK = "www.javahelps.com"
api_key = ""  # Fill your tinypg developer key here
FONT = 'font.ttf'


def getOpacity(img):
        # Calculate the opacity of watermark based on the image.
    rgbMedian = ImageStat.Stat(img).median
    totalAverage = sum(rgbMedian) / len(rgbMedian)
    opacity = math.ceil(totalAverage * 25.00 / 255.00) / 100.00
    return opacity


def add_watermark(img, text, angle=23):
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    size = 2
    n_font = ImageFont.truetype(FONT, size)
    n_width, n_height = n_font.getsize(text)
    while n_width + n_height < watermark.size[0]:
        size += 2
        n_font = ImageFont.truetype(FONT, size)
        n_width, n_height = n_font.getsize(text)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    draw.text(((watermark.size[0] - n_width) / 2,
               (watermark.size[1] - n_height) / 2),
              text, font=n_font)

    watermarkOpacity = getOpacity(img)
    watermark = watermark.rotate(angle, Image.BICUBIC)
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(watermarkOpacity)
    watermark.putalpha(alpha)

    return Image.composite(watermark, img, watermark)


def resize(img):
    # Width percent
    widthPercent = (BASE_WIDTH / float(img.size[0]))

    if widthPercent >= 1.0:
        return img

    # Expected height
    height = int((float(img.size[1]) * float(widthPercent)))

    # Resize it.
    resized = img.resize((BASE_WIDTH, height), Image.ANTIALIAS)
    return resized


# Let's parse the arguments.
opts, args = getopt.getopt(sys.argv[1:], 'd:')

# Set some default values to the needed variables.
directory = ''

# If an argument was passed in, assign it to the correct variable.
for opt, arg in opts:
    if opt == '-d':
        directory = arg

# We have to make sure that all of the arguments were passed.
if directory == '':
    print('Invalid command line argument. -d [directory] is required')

    # If an argument is missing exit the application.
    exit()

# Iterate through every image given in the directory argument and resize it.
for image in os.listdir(directory):
    print('Processing image ' + image)
    imgPath = os.path.join(directory, image)
    # Open the image file.
    img = Image.open(imgPath)

    # Add watermark
    watermark = add_watermark(img, WATERMARK)

    # Resize the imae
    img = resize(watermark)

    # Save it back to disk.
    img.save(os.path.join(directory, image), quality=95)

    # Compress image using tinypng.com
    shrink_info = shrink_file(imgPath, api_key, imgPath)
    print("Savings: {:.2%}".format(1 - shrink_info["output"]["ratio"]))

print('Batch processing complete.')
